# AdaptiveCruiseControl

The core ACC logic is ported (speed limit tracking, curvature limiting, following, gates/lights braking, PID, manual speed offset, lane-aware lead filtering). These pieces are missing because their providers are still not rewritten in c#:

- Prefab-aware traffic lights (“Normal” mode): In Python, ACC reads `tags.next_intersection` and `tags.next_intersection_lane` (emitted by `Plugins/Map`) and inspects prefab `nav_routes`/bounding boxes. No C# map/prefab provider or intersection tags exist yet.
- Tags/AR/debug overlays: Python publishes tags (`status`, `acc`, `acc_target`, `acc_gap`, `vehicle_highlights`, `vehicle_in_front_distance`, `light`, `stop_in`) and AR rectangles/text (via `Plugins/AR`). The C# host does not expose a tags/AR surface.
- Settings persistence/listen: Python uses `ETS2LASettings.listen` to persist and live-update settings (e.g., MU). C# uses in-memory settings; no persistence/listener API exists yet.
- Override/Takeover mapping: Python supports a tags-based override (`tags.override_acceleration`) and a `takeover` event. C# subscribes to `takeover` and an override channel, but until the host defines the canonical topics/tags, mapping is best-effort.
- Notifications: Python calls `notify` for user toasts on manual offset changes; C# only logs/uses a helper. Needs a UI toast API to match behavior.
- Gate/light states: Confirm semaphore enums match Python (lights state 1/2 = red/changing-to-red; gates state <3). Adjust filtering once the C# semaphores match the Python states.
- Lane projection fallback: Python’s in-lane check inserts an intermediate point when polyline distance starts increasing; the C# lane filter doesn’t implement this fallback yet.

1) The Map plugin’s prefab/intersection/nav-route data and tags (`next_intersection`, lane index, prefab bounds).
2) A tags/AR publish surface (from the AR plugin) for status/light/vehicle/highlight/debug output.
3) Settings persistence/listen like `ETS2LASettings`.
4) Canonical takeover/override topics/tags and a UI toast API.
