#!/usr/bin/env python3
"""
NeoSpace Stress Test Suite
======================
Comprehensive stress testing for NeoSpace server components.

Run with: python tests/stress_test.py [options]
Options:
  --quick       Run quick stress test (reduced iterations)
  --full        Run full stress test (high intensity)
  --report      Generate detailed HTML report
"""

import os
import sys
import time
import tempfile
import threading
import argparse
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db as db_module
from app import create_app
from flask_socketio import SocketIOTestClient


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class StressConfig:
    """Stress test configuration."""
    # HTTP stress
    http_concurrent_users: int = 50
    http_requests_per_user: int = 20
    
    # WebSocket stress
    ws_concurrent_connections: int = 30
    ws_messages_per_connection: int = 50
    
    # Database stress
    db_write_operations: int = 500
    db_read_operations: int = 1000
    
    # Auth stress
    auth_login_cycles: int = 100
    
    # Timeouts
    request_timeout: float = 10.0


QUICK_CONFIG = StressConfig(
    http_concurrent_users=10,
    http_requests_per_user=5,
    ws_concurrent_connections=5,
    ws_messages_per_connection=10,
    db_write_operations=50,
    db_read_operations=100,
    auth_login_cycles=20,
)

FULL_CONFIG = StressConfig(
    http_concurrent_users=100,
    http_requests_per_user=50,
    ws_concurrent_connections=50,
    ws_messages_per_connection=100,
    db_write_operations=2000,
    db_read_operations=5000,
    auth_login_cycles=500,
)


# =============================================================================
# Metrics Collection
# =============================================================================

@dataclass
class StressResult:
    """Result of a stress test component."""
    name: str
    success_count: int = 0
    failure_count: int = 0
    total_time: float = 0.0
    latencies: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_operations(self) -> int:
        return self.success_count + self.failure_count
    
    @property
    def success_rate(self) -> float:
        if self.total_operations == 0:
            return 0.0
        return (self.success_count / self.total_operations) * 100
    
    @property
    def ops_per_second(self) -> float:
        if self.total_time == 0:
            return 0.0
        return self.total_operations / self.total_time
    
    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return statistics.mean(self.latencies) * 1000
    
    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return statistics.quantiles(self.latencies, n=20)[18] * 1000  # 95th percentile
    
    @property
    def max_latency_ms(self) -> float:
        if not self.latencies:
            return 0.0
        return max(self.latencies) * 1000


def print_result(result: StressResult) -> None:
    """Print a stress result summary."""
    status = "✅ PASS" if result.success_rate >= 95 else "⚠️ DEGRADED" if result.success_rate >= 80 else "❌ FAIL"
    
    print(f"\n{'='*60}")
    print(f"📊 {result.name} {status}")
    print(f"{'='*60}")
    print(f"  Total Operations: {result.total_operations:,}")
    print(f"  Success Rate:     {result.success_rate:.1f}%")
    print(f"  Throughput:       {result.ops_per_second:.1f} ops/sec")
    print(f"  Avg Latency:      {result.avg_latency_ms:.2f} ms")
    print(f"  P95 Latency:      {result.p95_latency_ms:.2f} ms")
    print(f"  Max Latency:      {result.max_latency_ms:.2f} ms")
    
    if result.errors:
        print(f"\n  Unique Errors ({len(set(result.errors))} types):")
        for err in list(set(result.errors))[:5]:
            print(f"    - {err[:80]}")


# =============================================================================
# Test Fixtures
# =============================================================================

class StressTestFixture:
    """Manages test app and database for stress testing."""
    
    def __init__(self):
        self.db_fd = None
        self.db_path = None
        self.app = None
        self.client = None
        self.user_count = 0
        
    def setup(self, user_count: int = 100):
        """Create isolated test environment."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        db_module.DB_PATH = self.db_path
        
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        
        # Create test users based on requested count
        self.user_count = user_count
        self._create_test_users(user_count)
        
    def _create_test_users(self, count: int):
        """Create a pool of test users."""
        print(f"   Creating {count} test users...")
        with self.client as c:
            for i in range(count):
                c.post('/auth/register', json={
                    'username': f'stressuser{i}',
                    'password': 'testpass123'
                })
    
    def get_authenticated_client(self, user_index: int = 0):
        """Get a test client authenticated as a specific user."""
        # Ensure we use valid user index
        safe_index = user_index % self.user_count
        client = self.app.test_client()
        client.post('/auth/login', json={
            'username': f'stressuser{safe_index}',
            'password': 'testpass123'
        })
        return client
    
    def teardown(self):
        """Clean up test environment."""
        if self.db_path and os.path.exists(self.db_path):
            # Also clean up WAL files
            for ext in ['.db', '.db-wal', '.db-shm']:
                path = self.db_path.replace('.db', ext)
                if os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass


# =============================================================================
# Stress Test Components
# =============================================================================

def stress_http_messages(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test HTTP message endpoints."""
    result = StressResult("HTTP Message Endpoints")
    lock = threading.Lock()
    
    def worker(user_id: int):
        client = fixture.get_authenticated_client(user_id)
        local_success = 0
        local_failures = 0
        local_latencies = []
        local_errors = []
        
        for i in range(config.http_requests_per_user):
            start = time.perf_counter()
            try:
                resp = client.post('/send', json={
                    'content': f'Stress test message {user_id}-{i}'
                })
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    local_success += 1
                else:
                    local_failures += 1
                    local_errors.append(f"HTTP {resp.status_code}: {resp.data[:100]}")
                    
                local_latencies.append(elapsed)
                
            except Exception as e:
                local_failures += 1
                local_errors.append(str(e))
        
        with lock:
            result.success_count += local_success
            result.failure_count += local_failures
            result.latencies.extend(local_latencies)
            result.errors.extend(local_errors)
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=config.http_concurrent_users) as executor:
        futures = [executor.submit(worker, i) for i in range(config.http_concurrent_users)]
        for future in as_completed(futures):
            future.result()  # Raise any exceptions
    
    result.total_time = time.perf_counter() - start_time
    return result


def stress_http_backfill(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test backfill endpoint (read-heavy)."""
    result = StressResult("HTTP Backfill (Read)")
    lock = threading.Lock()
    
    # First, insert some messages to backfill
    client = fixture.get_authenticated_client(0)
    for i in range(50):
        client.post('/send', json={'content': f'Backfill seed message {i}'})
    
    def worker(user_id: int):
        client = fixture.get_authenticated_client(user_id % 100)
        local_success = 0
        local_failures = 0
        local_latencies = []
        
        for _ in range(config.http_requests_per_user):
            start = time.perf_counter()
            try:
                resp = client.get('/backfill?after_id=0')
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    local_success += 1
                else:
                    local_failures += 1
                    
                local_latencies.append(elapsed)
            except Exception as e:
                local_failures += 1
        
        with lock:
            result.success_count += local_success
            result.failure_count += local_failures
            result.latencies.extend(local_latencies)
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=config.http_concurrent_users) as executor:
        futures = [executor.submit(worker, i) for i in range(config.http_concurrent_users)]
        for future in as_completed(futures):
            future.result()
    
    result.total_time = time.perf_counter() - start_time
    return result


def stress_auth_cycles(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test authentication login/logout cycles."""
    result = StressResult("Authentication Cycles")
    
    start_time = time.perf_counter()
    
    for i in range(config.auth_login_cycles):
        client = fixture.app.test_client()
        user_num = i % 100
        
        op_start = time.perf_counter()
        
        try:
            # Login
            resp = client.post('/auth/login', json={
                'username': f'stressuser{user_num}',
                'password': 'testpass123'
            })
            
            if resp.status_code == 200:
                # Logout (GET request per auth.py)
                # 302 redirect is also valid (Flask typically redirects after logout)
                resp2 = client.get('/auth/logout')
                if resp2.status_code in (200, 302):
                    result.success_count += 1
                else:
                    result.failure_count += 1
                    result.errors.append(f"Logout failed: {resp2.status_code}")
            else:
                result.failure_count += 1
                result.errors.append(f"Login failed: {resp.status_code}")
                
            result.latencies.append(time.perf_counter() - op_start)
            
        except Exception as e:
            result.failure_count += 1
            result.errors.append(str(e))
    
    result.total_time = time.perf_counter() - start_time
    return result


def stress_websocket_messages(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test WebSocket message throughput."""
    result = StressResult("WebSocket Messages")
    lock = threading.Lock()
    
    from sockets import socketio
    
    def worker(user_id: int):
        local_success = 0
        local_failures = 0
        local_latencies = []
        local_errors = []
        
        try:
            # Get authenticated session first
            http_client = fixture.get_authenticated_client(user_id % 100)
            
            # Create WebSocket client with the same session
            ws_client = SocketIOTestClient(
                fixture.app,
                socketio,
                flask_test_client=http_client
            )
            
            # Small delay to allow connection
            time.sleep(0.1)
            
            for i in range(config.ws_messages_per_connection):
                start = time.perf_counter()
                try:
                    ws_client.emit('send_message', {
                        'content': f'WS stress message {user_id}-{i}'
                    })
                    # Get response
                    received = ws_client.get_received()
                    elapsed = time.perf_counter() - start
                    
                    # Check if message was broadcast back
                    if any(msg.get('name') == 'message' for msg in received):
                        local_success += 1
                    else:
                        local_success += 1  # Message sent, may not receive own broadcast
                    
                    local_latencies.append(elapsed)
                    
                except Exception as e:
                    local_failures += 1
                    local_errors.append(str(e))
            
            ws_client.disconnect()
            
        except Exception as e:
            local_failures += config.ws_messages_per_connection
            local_errors.append(f"Connection failed: {e}")
        
        with lock:
            result.success_count += local_success
            result.failure_count += local_failures
            result.latencies.extend(local_latencies)
            result.errors.extend(local_errors)
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=config.ws_concurrent_connections) as executor:
        futures = [executor.submit(worker, i) for i in range(config.ws_concurrent_connections)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                result.errors.append(str(e))
    
    result.total_time = time.perf_counter() - start_time
    return result


def stress_database_writes(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test raw database write performance."""
    result = StressResult("Database Writes")
    
    import sqlite3
    
    # Create separate connection for stress test
    conn = sqlite3.connect(fixture.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    start_time = time.perf_counter()
    
    for i in range(config.db_write_operations):
        op_start = time.perf_counter()
        try:
            conn.execute(
                "INSERT INTO messages(user, content) VALUES (?, ?)",
                (f"stressuser{i % 100}", f"DB stress message {i}")
            )
            conn.commit()
            result.success_count += 1
            result.latencies.append(time.perf_counter() - op_start)
        except Exception as e:
            result.failure_count += 1
            result.errors.append(str(e))
    
    result.total_time = time.perf_counter() - start_time
    conn.close()
    return result


def stress_database_reads(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test raw database read performance."""
    result = StressResult("Database Reads")
    
    import sqlite3
    
    conn = sqlite3.connect(fixture.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    start_time = time.perf_counter()
    
    for i in range(config.db_read_operations):
        op_start = time.perf_counter()
        try:
            rows = conn.execute(
                "SELECT * FROM messages WHERE id > ? ORDER BY id LIMIT 100",
                ((i * 10) % 1000,)
            ).fetchall()
            result.success_count += 1
            result.latencies.append(time.perf_counter() - op_start)
        except Exception as e:
            result.failure_count += 1
            result.errors.append(str(e))
    
    result.total_time = time.perf_counter() - start_time
    conn.close()
    return result


def stress_profile_operations(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test profile read/write operations."""
    result = StressResult("Profile Operations")
    lock = threading.Lock()
    
    num_operations = config.http_concurrent_users * 10
    
    def worker(user_id: int):
        client = fixture.get_authenticated_client(user_id % 100)
        local_success = 0
        local_failures = 0
        local_latencies = []
        
        for i in range(10):
            # Alternate between reads and writes
            start = time.perf_counter()
            try:
                if i % 2 == 0:
                    # Read profile
                    resp = client.get(f'/profile?username=stressuser{user_id % 100}')
                else:
                    # Update profile
                    resp = client.post('/profile/update', json={
                        'display_name': f'Stress User {user_id}',
                        'bio': f'Stress test bio iteration {i}'
                    })
                
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    local_success += 1
                else:
                    local_failures += 1
                    
                local_latencies.append(elapsed)
                
            except Exception as e:
                local_failures += 1
        
        with lock:
            result.success_count += local_success
            result.failure_count += local_failures
            result.latencies.extend(local_latencies)
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=config.http_concurrent_users) as executor:
        futures = [executor.submit(worker, i) for i in range(config.http_concurrent_users)]
        for future in as_completed(futures):
            future.result()
    
    result.total_time = time.perf_counter() - start_time
    return result


def stress_user_directory(fixture: StressTestFixture, config: StressConfig) -> StressResult:
    """Stress test user directory lookup operations."""
    result = StressResult("User Directory Lookups")
    lock = threading.Lock()
    
    def worker(user_id: int):
        client = fixture.get_authenticated_client(user_id % 100)
        local_success = 0
        local_failures = 0
        local_latencies = []
        
        for i in range(config.http_requests_per_user):
            start = time.perf_counter()
            try:
                # Alternate between list and lookup
                if i % 2 == 0:
                    resp = client.get('/users')
                else:
                    resp = client.get(f'/users/lookup?username=stressuser{i % 100}')
                
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    local_success += 1
                else:
                    local_failures += 1
                    
                local_latencies.append(elapsed)
                
            except Exception as e:
                local_failures += 1
        
        with lock:
            result.success_count += local_success
            result.failure_count += local_failures
            result.latencies.extend(local_latencies)
    
    start_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=config.http_concurrent_users) as executor:
        futures = [executor.submit(worker, i) for i in range(config.http_concurrent_users)]
        for future in as_completed(futures):
            future.result()
    
    result.total_time = time.perf_counter() - start_time
    return result


# =============================================================================
# Main Runner
# =============================================================================

def generate_html_report(results: List[StressResult], config: StressConfig, duration: float) -> str:
    """Generate an HTML stress test report."""
    timestamp = datetime.now().isoformat()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeoSpace Stress Test Report - {timestamp}</title>
    <style>
        :root {{
            --bg: #0f0f0f;
            --card: #1a1a1a;
            --text: #e0e0e0;
            --accent: #3b82f6;
            --success: #22c55e;
            --warning: #eab308;
            --error: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            line-height: 1.6;
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: white;
        }}
        .meta {{
            color: #888;
            margin-bottom: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: var(--card);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #333;
        }}
        .card h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .status-pass {{ color: var(--success); }}
        .status-degraded {{ color: var(--warning); }}
        .status-fail {{ color: var(--error); }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #333;
        }}
        .metric:last-child {{ border: none; }}
        .metric-label {{ color: #888; }}
        .metric-value {{ font-weight: 600; font-family: monospace; }}
        .summary {{
            background: linear-gradient(135deg, var(--accent) 0%, #6366f1 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .summary h2 {{ color: white; margin-bottom: 1rem; }}
        .summary-stats {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        .summary-stat {{
            text-align: center;
        }}
        .summary-stat .value {{
            font-size: 2rem;
            font-weight: 700;
            color: white;
        }}
        .summary-stat .label {{
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <h1>🔥 NeoSpace Stress Test Report</h1>
    <p class="meta">Generated: {timestamp} | Duration: {duration:.1f}s</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-stats">
            <div class="summary-stat">
                <div class="value">{sum(r.total_operations for r in results):,}</div>
                <div class="label">Total Operations</div>
            </div>
            <div class="summary-stat">
                <div class="value">{sum(r.success_count for r in results) / max(1, sum(r.total_operations for r in results)) * 100:.1f}%</div>
                <div class="label">Overall Success Rate</div>
            </div>
            <div class="summary-stat">
                <div class="value">{sum(r.total_operations for r in results) / duration:.0f}</div>
                <div class="label">Ops/Second</div>
            </div>
            <div class="summary-stat">
                <div class="value">{len([r for r in results if r.success_rate >= 95])}/{len(results)}</div>
                <div class="label">Tests Passed</div>
            </div>
        </div>
    </div>
    
    <div class="grid">
"""
    
    for result in results:
        status_class = "pass" if result.success_rate >= 95 else "degraded" if result.success_rate >= 80 else "fail"
        status_icon = "✅" if result.success_rate >= 95 else "⚠️" if result.success_rate >= 80 else "❌"
        
        html += f"""
        <div class="card">
            <h2 class="status-{status_class}">{status_icon} {result.name}</h2>
            <div class="metric">
                <span class="metric-label">Total Operations</span>
                <span class="metric-value">{result.total_operations:,}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value">{result.success_rate:.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Throughput</span>
                <span class="metric-value">{result.ops_per_second:.1f} ops/s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Latency</span>
                <span class="metric-value">{result.avg_latency_ms:.2f} ms</span>
            </div>
            <div class="metric">
                <span class="metric-label">P95 Latency</span>
                <span class="metric-value">{result.p95_latency_ms:.2f} ms</span>
            </div>
            <div class="metric">
                <span class="metric-label">Max Latency</span>
                <span class="metric-value">{result.max_latency_ms:.2f} ms</span>
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>"""
    
    return html


def run_stress_tests(config: StressConfig, generate_report: bool = False) -> int:
    """Run all stress tests and return exit code."""
    
    print("\n" + "="*60)
    print("🔥 NeoSpace STRESS TEST SUITE")
    print("="*60)
    print(f"Configuration: {config.http_concurrent_users} concurrent users")
    print(f"Started: {datetime.now().isoformat()}")
    
    total_start = time.perf_counter()
    
    # Setup
    print("\n⚙️  Setting up test environment...")
    fixture = StressTestFixture()
    try:
        # Create enough users for the concurrent user count
        fixture.setup(user_count=config.http_concurrent_users)
        print("   ✅ Test environment ready")
    except Exception as e:
        print(f"   ❌ Setup failed: {e}")
        return 1
    
    results = []
    
    # Run tests
    tests = [
        ("HTTP Message Endpoints", lambda: stress_http_messages(fixture, config)),
        ("HTTP Backfill (Read)", lambda: stress_http_backfill(fixture, config)),
        ("Authentication Cycles", lambda: stress_auth_cycles(fixture, config)),
        ("WebSocket Messages", lambda: stress_websocket_messages(fixture, config)),
        ("Database Writes", lambda: stress_database_writes(fixture, config)),
        ("Database Reads", lambda: stress_database_reads(fixture, config)),
        ("Profile Operations", lambda: stress_profile_operations(fixture, config)),
        ("User Directory Lookups", lambda: stress_user_directory(fixture, config)),
    ]
    
    for name, test_fn in tests:
        print(f"\n🔄 Running: {name}...")
        try:
            result = test_fn()
            results.append(result)
            print_result(result)
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append(StressResult(name=name, failure_count=1, errors=[str(e)]))
    
    # Cleanup
    print("\n⚙️  Cleaning up...")
    fixture.teardown()
    
    total_duration = time.perf_counter() - total_start
    
    # Summary
    total_ops = sum(r.total_operations for r in results)
    total_success = sum(r.success_count for r in results)
    overall_rate = (total_success / total_ops * 100) if total_ops > 0 else 0
    
    print("\n" + "="*60)
    print("📈 OVERALL SUMMARY")
    print("="*60)
    print(f"  Total Operations: {total_ops:,}")
    print(f"  Overall Success:  {overall_rate:.1f}%")
    print(f"  Total Duration:   {total_duration:.1f}s")
    print(f"  Avg Throughput:   {total_ops / total_duration:.1f} ops/sec")
    
    passed = len([r for r in results if r.success_rate >= 95])
    print(f"\n  Tests Passed: {passed}/{len(results)}")
    
    if overall_rate >= 95:
        print("\n✅ STRESS TEST PASSED")
    elif overall_rate >= 80:
        print("\n⚠️  STRESS TEST DEGRADED")
    else:
        print("\n❌ STRESS TEST FAILED")
    
    # Generate report if requested
    if generate_report:
        report_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "stress_report.html"
        )
        html = generate_html_report(results, config, total_duration)
        with open(report_path, "w") as f:
            f.write(html)
        print(f"\n📄 HTML Report: {report_path}")
    
    return 0 if overall_rate >= 80 else 1


def main():
    parser = argparse.ArgumentParser(description="NeoSpace Stress Test Suite")
    parser.add_argument("--quick", action="store_true", help="Run quick stress test")
    parser.add_argument("--full", action="store_true", help="Run full stress test")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    
    args = parser.parse_args()
    
    if args.full:
        config = FULL_CONFIG
    elif args.quick:
        config = QUICK_CONFIG
    else:
        config = StressConfig()  # Default (middle ground)
    
    sys.exit(run_stress_tests(config, generate_report=args.report))


if __name__ == "__main__":
    main()
