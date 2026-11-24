"""
Generates high-resolution architecture diagrams for Cloud-Based Student Management System.
Creates architecture_diagram.png.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
fig.patch.set_facecolor('#0f172a')  # Slate 900 dark background
ax.set_facecolor('#0f172a')

# Title & Subtitle
ax.text(7, 8.55, "Cloud-Based Student Management System", 
        fontsize=20, weight='bold', color='#ffffff', ha='center', va='center')
ax.text(7, 8.2, "Kubernetes Microservices Architecture with Auto-Scaling (HPA) & Self-Healing", 
        fontsize=12, color='#94a3b8', ha='center', va='center')

def draw_box(x, y, w, h, bg_color, border_color, title, subtitle="", icon="", radius=0.2):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.08,rounding_size={radius}",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=2)
    ax.add_patch(rect)
    center_x = x + w/2
    if subtitle:
        ax.text(center_x, y + h*0.62, title, fontsize=10.5, weight='bold', color='#ffffff', ha='center', va='center')
        ax.text(center_x, y + h*0.32, subtitle, fontsize=8.5, color='#cbd5e1', ha='center', va='center')
    else:
        ax.text(center_x, y + h*0.5, title, fontsize=10.5, weight='bold', color='#ffffff', ha='center', va='center')

def draw_container_boundary(x, y, w, h, title, border_color="#334155", bg_color="#1e293b"):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.3",
                                  facecolor=bg_color, edgecolor=border_color, linewidth=1.8, linestyle='--')
    ax.add_patch(rect)
    ax.text(x + 0.3, y + h - 0.35, title, fontsize=11, weight='bold', color='#38bdf8', ha='left', va='center')

def draw_arrow(x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45",
                                color="#38bdf8", lw=2, shrinkA=4, shrinkB=4))
    if label:
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my + 0.18, label, fontsize=8, color='#38bdf8', weight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='#0f172a', edgecolor='none'))

# 1. Tier: Users / Clients (Left)
draw_box(0.5, 4.8, 2.2, 1.2, "#1e3a8a", "#60a5fa", "Web Browsers", "HTTP / REST Clients\n(Port 80/443)")
draw_box(0.5, 2.8, 2.2, 1.2, "#312e81", "#818cf8", "Load Test Agent", "wrk / ApacheBench\n(Traffic Generator)")

# 2. Tier: Ingress & K8s Service
draw_box(3.5, 3.8, 2.2, 1.6, "#047857", "#34d178", "Kubernetes Service", "Type: NodePort / LB\nstudent-app-service\nPort: 80 -> 5000")

# 3. K8s Cluster Boundary
draw_container_boundary(6.2, 0.6, 7.3, 7.0, "Kubernetes Cluster (Namespace: student-system)")

# App Deployment Sub-boundary
draw_container_boundary(6.5, 3.7, 4.4, 3.5, "Deployment: student-app (Replicas: 2..8)", border_color="#3b82f6", bg_color="#0f172a")

# Pod 1 & Pod 2
draw_box(6.8, 5.2, 3.8, 1.0, "#1d4ed8", "#93c5fd", "student-app Pod 1", "Flask + Gunicorn | /health | Port 5000")
draw_box(6.8, 4.0, 3.8, 1.0, "#1d4ed8", "#93c5fd", "student-app Pod 2", "Flask + Gunicorn | /health | Port 5000")

# HPA Controller
draw_box(11.2, 5.2, 2.1, 1.6, "#c2410c", "#fb923c", "HPA Controller", "student-app-hpa\nTarget: CPU > 50%\nMin: 2 | Max: 8")

# ConfigMap & Secret
draw_box(6.5, 2.3, 4.4, 0.9, "#374151", "#9ca3af", "ConfigMap & Secrets", "POSTGRES_HOST, DB, USER, PASS")

# PostgreSQL Stateful Tier
draw_container_boundary(6.5, 0.9, 4.4, 1.1, "Database Tier: postgres-deployment", border_color="#059669", bg_color="#0f172a")
draw_box(6.7, 1.0, 2.0, 0.8, "#065f46", "#6ee7b7", "PostgreSQL Pod", "Port 5432")
draw_box(8.9, 1.0, 1.8, 0.8, "#0f766e", "#5eead4", "PersistentVolume", "postgres-pvc (2Gi)")

# Connectors
draw_arrow(2.7, 5.4, 3.5, 4.9, "User Traffic")
draw_arrow(2.7, 3.4, 3.5, 4.3, "Stress Load")

draw_arrow(5.7, 4.9, 6.8, 5.5, "Round-Robin")
draw_arrow(5.7, 4.3, 6.8, 4.5, "Round-Robin")

# HPA arrows
draw_arrow(11.2, 5.7, 10.6, 5.7, "Auto-scale")
draw_arrow(10.6, 4.5, 11.2, 5.3, "Metrics Feed")

# DB arrows
draw_arrow(8.7, 4.0, 8.7, 3.2, "Fetch Env")
draw_arrow(7.7, 3.2, 7.7, 1.8, "SQL Queries")
draw_arrow(8.7, 1.4, 8.9, 1.4, "Mounts")

# Footer Badges
badge_y = 0.25
ax.text(2.0, badge_y, "[x] High Availability", fontsize=9.5, color='#4ade80', weight='bold', ha='center')
ax.text(5.5, badge_y, "[x] Self-Healing ReplicaSet", fontsize=9.5, color='#4ade80', weight='bold', ha='center')
ax.text(9.0, badge_y, "[x] Horizontal Auto-Scaling (HPA)", fontsize=9.5, color='#4ade80', weight='bold', ha='center')
ax.text(12.3, badge_y, "[x] Persistent Storage", fontsize=9.5, color='#4ade80', weight='bold', ha='center')

ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')

plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
print("Successfully generated architecture_diagram.png")
