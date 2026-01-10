/**
 * WallNetwork.js
 * API calls for the Wall.
 * Pure module - returns data, does not render.
 */

import { state, setCurrentUserData } from './WallState.js';

// DOM Elements are queried continuously to avoid stale references/nulls on early load
function getLoadingEl() { return document.getElementById('loading'); }
function getWallContainer() { return document.getElementById('wall-container'); }

export async function fetchProfileData() {
    const endpoint = state.userId ? `/profile?user_id=${state.userId}` : '/profile';
    try {
        const res = await fetch(endpoint);
        if (res.status === 401) {
            window.location.href = '/auth/login';
            return null;
        }

        let data;
        try {
            data = await res.json();
        } catch (jsonErr) {
            throw new Error("Invalid JSON response from server");
        }

        if (data.error) {
            const el = getLoadingEl();
            if (el) el.innerHTML = `<div class="text-red-400 font-bold border-2 border-red-500 p-4 bg-white shadow-hard">${data.error}</div>`;
            return null;
        }

        setCurrentUserData(data);

        const el = getLoadingEl();
        const wc = getWallContainer();
        if (el) el.classList.add('hidden');
        if (wc) wc.classList.remove('hidden');

        return data;

    } catch (err) {
        console.error(err);
        const el = getLoadingEl();
        if (el) el.innerHTML = `
            <div class="text-red-500 font-bold border-2 border-red-500 p-4 bg-white shadow-hard flex flex-col items-center gap-2">
                <i class="ph-bold ph-warning-octagon text-3xl"></i>
                <span>CONNECTION LOST</span>
                <span class="text-xs font-mono text-black">${err.message || 'Unknown Error'}</span>
                <button onclick="window.location.reload()" class="mt-2 px-4 py-1 bg-black text-white text-xs font-bold uppercase hover:bg-gray-800">Retry</button>
            </div>`;
        return null;
    }
}

export async function deleteModule(moduleId) {
    try {
        const res = await fetch('/wall/post/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
            },
            body: JSON.stringify({ id: moduleId })
        });
        const data = await res.json();
        return data;
    } catch (e) {
        console.error(e);
        return { ok: false, error: 'Network error' };
    }
}

export async function fetchScriptContent(scriptId) {
    const res = await fetch(`/scripts/get?id=${scriptId}`);
    return await res.json();
}

export async function fetchMorePosts(profileId, page) {
    try {
        const res = await fetch(`/wall/posts/${profileId}?page=${page}&limit=20`);
        return await res.json();
    } catch (e) {
        console.error(e);
        return null;
    }
}
