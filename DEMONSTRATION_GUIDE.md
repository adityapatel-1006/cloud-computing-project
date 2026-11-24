# Demonstration Guide & Screenshot Verification
## Project: Cloud-Based Student Management System

This guide provides exact commands, execution procedures, and sample terminal outputs for capturing the **four required screenshots** for your project submission:
1. **Running Pods & Services**
2. **Self-Healing Demonstration**
3. **Horizontal Pod Autoscaler (HPA) Scaling**
4. **Failover & High Availability**

---

### Prerequisites
Make sure your Kubernetes cluster is active (Docker Desktop Kubernetes, Minikube, Kind, or AWS EKS / GCP GKE):
```bash
# 1. Apply Kubernetes manifests
kubectl apply -f k8s.yaml
kubectl apply -f hpa.yaml

# 2. Verify all components are created in the student-system namespace
kubectl get all -n student-system
```

---

### Screenshot 1: Running Pods, Services, and Persistent Storage
**Goal:** Prove that the microservices architecture, application pods, database, and networking services are running and healthy.

#### Command:
```bash
kubectl get pods,svc,deploy,pvc,hpa -n student-system -o wide
```

#### Expected Terminal Output for Screenshot:
```text
NAME                                           READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
pod/postgres-deployment-64d858cfd6-r7k9x       1/1     Running   0          5m    10.244.0.5   node-01    <none>           <none>
pod/student-app-deployment-7bb948c966-2lm4b   1/1     Running   0          5m    10.244.0.6   node-01    <none>           <none>
pod/student-app-deployment-7bb948c966-9wz2x   1/1     Running   0          5m    10.244.0.7   node-02    <none>           <none>

NAME                          TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE   SELECTOR
service/postgres-service      ClusterIP   10.96.142.88     <none>        5432/TCP       5m    app=postgres-db
service/student-app-service   NodePort    10.103.220.14    <none>        80:30080/TCP   5m    app=student-app

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS    IMAGES
deployment.apps/postgres-deployment      1/1     1            1           5m    postgres      postgres:15-alpine
deployment.apps/student-app-deployment   2/2     2            2           5m    student-app   student-management-app:latest

NAME                                                 STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/postgres-pvc                   Bound    pvc-8789520b-e66b-4375-9c17-48f074d22223   2Gi        RWO            standard       5m

NAME                                                  REFERENCE                           TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/student-app-hpa   Deployment/student-app-deployment   cpu: 4%/50%     2         8         2          5m
```

📸 **Screenshot Action:** Capture the terminal displaying all pods in `Running (1/1)` status, bound PVC, and active NodePort service.

---

### Screenshot 2: Self-Healing Demonstration
**Goal:** Demonstrate Kubernetes automated self-healing. When an active application pod is terminated or crashes, the ReplicaSet immediately provisions a replacement pod without manual intervention.

#### Step 1: Watch pods in a separate terminal:
```bash
kubectl get pods -n student-system -w
```

#### Step 2: Delete one of the running application pods:
```bash
kubectl delete pod student-app-deployment-7bb948c966-2lm4b -n student-system
```

#### Expected Terminal Output for Screenshot:
```text
$ kubectl get pods -n student-system
NAME                                          READY   STATUS    RESTARTS   AGE
postgres-deployment-64d858cfd6-r7k9x          1/1     Running   0          8m
student-app-deployment-7bb948c966-2lm4b      1/1     Running   0          8m
student-app-deployment-7bb948c966-9wz2x      1/1     Running   0          8m

$ kubectl delete pod student-app-deployment-7bb948c966-2lm4b -n student-system
pod "student-app-deployment-7bb948c966-2lm4b" deleted

$ kubectl get pods -n student-system
NAME                                          READY   STATUS              RESTARTS   AGE
postgres-deployment-64d858cfd6-r7k9x          1/1     Running             0          8m30s
student-app-deployment-7bb948c966-2lm4b      1/1     Terminating         0          8m30s
student-app-deployment-7bb948c966-9wz2x      1/1     Running             0          8m30s
student-app-deployment-7bb948c966-x7v4q      0/1     ContainerCreating   0          2s

$ kubectl get pods -n student-system
NAME                                          READY   STATUS    RESTARTS   AGE
postgres-deployment-64d858cfd6-r7k9x          1/1     Running   0          8m45s
student-app-deployment-7bb948c966-9wz2x      1/1     Running   0          8m45s
student-app-deployment-7bb948c966-x7v4q      1/1     Running   0          17s
```

📸 **Screenshot Action:** Capture the terminal showing `Terminating` on the old pod and `ContainerCreating` / `Running (1/1)` on the newly created replacement pod (`x7v4q`).

---

### Screenshot 3: Horizontal Pod Autoscaler (HPA) Scaling
**Goal:** Demonstrate dynamic horizontal auto-scaling when CPU load exceeds the target threshold (50%).

#### Step 1: Open Terminal 1 and watch the HPA status:
```bash
kubectl get hpa student-app-hpa -n student-system -w
```

#### Step 2: Generate load from Terminal 2:
You can click the **"Simulate High CPU"** button directly on the Web UI, or execute the following curl commands in a loop:
```bash
# Generate computational load across pods
for i in {1..20}; do
  curl -s -X POST http://localhost:30080/api/load -H "Content-Type: application/json" -d '{"duration": 30}' &
done
```

#### Expected Terminal Output for Screenshot:
```text
$ kubectl get hpa student-app-hpa -n student-system -w
NAME              REFERENCE                           TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
student-app-hpa   Deployment/student-app-deployment   cpu: 4%/50%     2         8         2          10m
student-app-hpa   Deployment/student-app-deployment   cpu: 38%/50%    2         8         2          11m
student-app-hpa   Deployment/student-app-deployment   cpu: 84%/50%    2         8         2          11m15s
student-app-hpa   Deployment/student-app-deployment   cpu: 84%/50%    2         8         4          11m30s
student-app-hpa   Deployment/student-app-deployment   cpu: 76%/50%    2         8         6          12m

$ kubectl get pods -n student-system
NAME                                          READY   STATUS    RESTARTS   AGE
postgres-deployment-64d858cfd6-r7k9x          1/1     Running   0          15m
student-app-deployment-7bb948c966-9wz2x      1/1     Running   0          15m
student-app-deployment-7bb948c966-x7v4q      1/1     Running   0          7m
student-app-deployment-7bb948c966-k4b12      1/1     Running   0          45s
student-app-deployment-7bb948c966-m9p88      1/1     Running   0          45s
student-app-deployment-7bb948c966-p0q11      1/1     Running   0          15s
student-app-deployment-7bb948c966-w2e33      1/1     Running   0          15s
```

📸 **Screenshot Action:** Capture `kubectl get hpa` showing CPU utilization surging past 50% (e.g. `84%/50%`) and the replica count automatically scaling from `2` to `6` pods.

---

### Screenshot 4: Failover & High Availability Demonstration
**Goal:** Verify zero-downtime failover by continuously querying the `/health` endpoint while intentionally killing an active replica.

#### Step 1: In Terminal 1, run a continuous health-probe loop:
```bash
while true; do curl -s http://localhost:30080/health | grep -o '"pod_name":"[^"]*' ; sleep 0.5; done
```

#### Step 2: In Terminal 2, kill one of the active app pods:
```bash
kubectl delete pod student-app-deployment-7bb948c966-9wz2x -n student-system --now
```

#### Expected Terminal Output for Screenshot:
```text
$ while true; do curl -s http://localhost:30080/health | grep -o '"status":"[^"]*","pod_name":"[^"]*"' ; sleep 0.5; done
"status":"UP","pod_name":"student-app-deployment-7bb948c966-9wz2x"
"status":"UP","pod_name":"student-app-deployment-7bb948c966-x7v4q"
"status":"UP","pod_name":"student-app-deployment-7bb948c966-9wz2x"
"status":"UP","pod_name":"student-app-deployment-7bb948c966-x7v4q"
[Pod deleted in Terminal 2]
"status":"UP","pod_name":"student-app-deployment-7bb948c966-x7v4q"
"status":"UP","pod_name":"student-app-deployment-7bb948c966-x7v4q"
"status":"UP","pod_name":"student-app-deployment-7bb948c966-newpod1"
"status":"UP","pod_name":"student-app-deployment-7bb948c966-x7v4q"
```

*Note: Notice how 100% of requests continue returning `"status":"UP"` with zero dropped connections or 502/503 errors. The Kubernetes Service immediately reroutes all traffic to healthy pods.*

📸 **Screenshot Action:** Capture the continuous stream of successful `"status":"UP"` responses transitioning across pod instances with zero errors during the pod termination.
