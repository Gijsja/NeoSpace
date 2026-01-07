# User Journey Map: The Creator Flow

**Scenario**: Creating and Publishing an Interactive 3D Sketch
**Persona**: "Alex" (Creative Coder)
**Platform**: NeoSpace (Creative OS)

---

## 1. The Spark (Discovery & Entry)

**Goal**: Alex wants to share a visual idea (a "breathing" neon cube) they just conceived.
**Context**: Late night, desktop environment.

| Step    | User Action                                   | Touchpoint            | Emotional State      | System Response                                                                         |
| :------ | :-------------------------------------------- | :-------------------- | :------------------- | :-------------------------------------------------------------------------------------- |
| **1.1** | Alex opens NeoSpace.                          | **Unified Dashboard** | 😐 Neutral (Routine) | App connects instantly. Socket "Synced" status glows green.                             |
| **1.2** | Sees "Code Mode" toggle in the context panel. | **Context Sidebar**   | 🧐 Curious           | Tooltip: "Enter Creative Sandbox".                                                      |
| **1.3** | Clicks "Code Mode".                           | **Transition**        | 🤩 Anticipation      | Interface morphs. Chat recedes. Editor slides in. "Safe Mode" badge verifies isolation. |

---

## 2. The Studio (Creation & Iteration)

**Goal**: Translate the mental image into executing code.
**Barrier**: Syntax errors, API friction.

| Step    | User Action                                      | Touchpoint           | Emotional State | System Response                                                            |
| :------ | :----------------------------------------------- | :------------------- | :-------------- | :------------------------------------------------------------------------- |
| **2.1** | Selects "Three.js" from library picker.          | **Creative Editor**  | 🧠 Focused      | Editor loads boilerplate geometry instantly. Canvas shows a spinning cube. |
| **2.2** | Modifies `cube.geometry` to `icosahedron`.       | **Code Editor**      | 🔧 Constructive | Live Canvas updates in real-time (Hot Reload).                             |
| **2.3** | Adds a loop to pulse scale based on `sin(time)`. | **Code Editor**      | 😨 Anxiety      | **Error**: "Undefined variable 'time'". Console highlights line 24.        |
| **2.4** | Fixes variable name. Clicks "Run".               | **Console / Canvas** | 😌 Relief       | Sphere begins "breathing" neon green. The vision is realized.              |

---

## 3. The Release (Publishing)

**Goal**: Share the creation with the #generative-art room.
**Motivation**: Social validation, belonging.

| Step    | User Action                                  | Touchpoint        | Emotional State | System Response                                            |
| :------ | :------------------------------------------- | :---------------- | :-------------- | :--------------------------------------------------------- |
| **3.1** | Clicks "Publish" button.                     | **Action Bar**    | 🤞 Hopeful      | Modal appears: "Add a caption/tags".                       |
| **3.2** | Types "Neon breathing experiment. #threejs". | **Modal**         | ✍️ Expressive   | Inputs validated. Preview card shown.                      |
| **3.3** | Selects destination: "#generative-art".      | **Room Selector** | 🚀 Committed    | Sketch wraps into an **Interactive Card**. Posted to feed. |

---

## 4. Resonance (Feedback Loop)

**Goal**: Receive acknowledgement and connection.
**Opportunity**: "Stickers" as distinct, high-value feedback.

| Step    | User Action                                        | Touchpoint       | Emotional State | System Response                                                      |
| :------ | :------------------------------------------------- | :--------------- | :-------------- | :------------------------------------------------------------------- |
| **4.1** | Alex returns to the **Unified Dashboard**.         | **Main Chat**    | 😨 Vulnerable   | Feed shows the post live. Other users' avatars hover near it.        |
| **4.2** | Notification: "Sarah stuck a '🔥' on your sketch". | **Toast / Card** | 😍 Gratitude    | A 'Fire' sticker physically adheres to the corner of the post frame. |
| **4.3** | Another user forks the code via "View Source".     | **System Event** | 🤝 Connected    | Notification: "Dave is remixing your sketch".                        |

---

## Design Principles at Work

- **Seamless Mode Switching**: No jarring page loads between Chat and Code. The "OS" feel keeps Alex immersed.
- **Radical Speed**: Hot-reloading in the editor removes the feedback gap, keeping Alex in the "Flow State".
- **Tangible Feedback**: Stickers aren't just counters; they are _objects_ that accumulate on the work, mimicking a physical gallery guestbook.
