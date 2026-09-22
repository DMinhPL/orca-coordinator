# Developer Infrastructure and Distributed Runtime

Load for Docker, Kubernetes, proxies, load balancers, CDN, Redis, deployment, or multi-instance behavior.

Check:
- readiness vs liveness and traffic timing;
- graceful shutdown/draining;
- old/new version coexistence during rolling deploy;
- sticky-session assumptions and first-request behavior;
- shared vs instance-local state;
- cache key/version/invalidation semantics;
- CDN/proxy/browser cache layers independently;
- environment/config differences;
- request correlation and instance identity in evidence.

Do not treat sticky sessions as a substitute for shared consistency where requests/assets can reach different instances.
