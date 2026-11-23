"""Frontend Gradio: cliente que consume la API FastAPI.

Pantalla principal con pestanas:
  - Ingreso / registro
  - Fincas y lotes
  - Cultivos
  - Carga y analisis de imagenes (clasificador visual)
  - Historial de inferencias
  - Panel de incidencias
"""
from __future__ import annotations

from typing import Optional

import gradio as gr
import httpx

from backend.config import settings

API_URL = f"http://127.0.0.1:{settings.api_port}"


class ApiClient:
    """Cliente minimo contra la API FastAPI."""

    def __init__(self):
        self.token: Optional[str] = None
        self.role: Optional[str] = None
        self.username: Optional[str] = None

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def login(self, username: str, password: str):
        r = httpx.post(f"{API_URL}/auth/login", data={"username": username, "password": password}, timeout=10)
        r.raise_for_status()
        self.token = r.json()["access_token"]
        me = httpx.get(f"{API_URL}/auth/me", headers=self.headers, timeout=10).json()
        self.role = me["role"]
        self.username = me["username"]
        return me

    def register(self, username, email, password, role):
        r = httpx.post(f"{API_URL}/auth/register", json={
            "username": username, "email": email, "password": password, "role": role,
        }, timeout=10)
        r.raise_for_status()
        return r.json()

    def get(self, path, params=None):
        r = httpx.get(f"{API_URL}{path}", headers=self.headers, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def post(self, path, json=None, files=None, params=None):
        r = httpx.post(f"{API_URL}{path}", headers=self.headers, json=json, files=files, params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def patch(self, path, json=None):
        r = httpx.patch(f"{API_URL}{path}", headers=self.headers, json=json, timeout=30)
        r.raise_for_status()
        return r.json()


client = ApiClient()


# ---------- Helpers de UI ----------
def do_login(username, password):
    try:
        client.login(username, password)
        return f"Sesion iniciada como {client.username} ({client.role})", gr.update(visible=False), gr.update(visible=True)
    except Exception as e:
        return f"Error: {e}", gr.update(visible=True), gr.update(visible=False)

def do_logout():
    client.token = None
    client.role = None
    client.username = None

    return (
        gr.update(visible=True),
        gr.update(visible=False),
        "Sesión cerrada correctamente. Puedes ingresar con otro usuario."
    )    


def do_register(username, email, password, role):
    try:
        client.register(username, email, password, role)
        return f"Usuario {username} creado. Ahora inicia sesion."
    except Exception as e:
        return f"Error: {e}"


def list_farms():
    try:
        rows = client.get("/farms")
        return [[f["id"], f["name"], f.get("location", ""), f.get("area_ha", "")] for f in rows]
    except Exception as e:
        return [[f"Error: {e}", "", "", ""]]


def create_farm(name, location, area_ha):
    if not name or not name.strip():
        raise gr.Error("El nombre de la finca es obligatorio")
    try:
        payload = {"name": name, "location": location or None, "area_ha": float(area_ha) if area_ha else None}
        client.post("/farms", json=payload)
        return "Finca creada", list_farms()
    except Exception as e:
        return f"Error: {e}", list_farms()


def list_lots():
    try:
        rows = client.get("/lots")
        return [[l["id"], l["farm_id"], l["name"], l.get("area_m2", "")] for l in rows]
    except Exception as e:
        return [[f"Error: {e}", "", "", ""]]


def create_lot(farm_id, name, area_m2, description):
    if not name or not name.strip():
        raise gr.Error("El nombre del lote es obligatorio")
    try:
        payload = {"farm_id": int(farm_id), "name": name,
                   "area_m2": float(area_m2) if area_m2 else None,
                   "description": description or None}
        client.post("/lots", json=payload)
        return "Lote creado", list_lots()
    except Exception as e:
        return f"Error: {e}", list_lots()


def list_crops():
    try:
        rows = client.get("/crops")
        return [[c["id"], c["lot_id"], c["species"], c.get("variety", "")] for c in rows]
    except Exception as e:
        return [[f"Error: {e}", "", "", ""]]


def create_crop(lot_id, species, variety):
    if not species or not species.strip():
        raise gr.Error("La especie del cultivo es obligatoria")
    try:
        payload = {"lot_id": int(lot_id), "species": species, "variety": variety or None}
        client.post("/crops", json=payload)
        return "Cultivo creado", list_crops()
    except Exception as e:
        return f"Error: {e}", list_crops()


def analyze_image(image_file, crop_id):
    if image_file is None:
        return "Debes subir una imagen", None, None
    try:
        with open(image_file, "rb") as f:
            files = {"file": (image_file.split("/")[-1], f, "image/jpeg")}
            params = {"crop_id": int(crop_id)} if crop_id else None
            img = client.post("/images", files=files, params=params)
        inf = client.post(f"/images/{img['id']}/analyze")
        resumen = (
            f"Hojas detectadas: {inf['n_leaves_detected']} "
            f"(sana: {inf['n_sana']}, mancha: {inf['n_mancha']}, seca: {inf['n_seca']})\n"
            f"Confianza media: {inf['avg_confidence']:.2f}\n"
            f"Tiempo: {inf['inference_time_ms']} ms\n"
            f"Modelo: {inf['model_version']}"
        )
        annotated = inf.get("annotated_path") or None
        return resumen, annotated, inf
    except Exception as e:
        return f"Error: {e}", None, None


def list_inferences():
    try:
        rows = client.get("/inferences")
        return [[r["id"], r["image_id"], r["n_leaves_detected"],
                 r["n_sana"], r["n_mancha"], r["n_seca"],
                 f"{r['avg_confidence']:.2f}", r["expert_reviewed"]] for r in rows]
    except Exception as e:
        return [[f"Error: {e}", "", "", "", "", "", "", ""]]


def review_inference(inf_id, reviewed, notes):
    try:
        client.patch(f"/inferences/{int(inf_id)}/review",
                     json={"expert_reviewed": bool(reviewed), "expert_notes": notes or None})
        return "Revision guardada", list_inferences()
    except Exception as e:
        return f"Error: {e}", list_inferences()


def list_incidents(status_filter, severity):
    try:
        params = {}
        if status_filter and status_filter != "todas":
            params["status_filter"] = status_filter
        if severity and severity != "todas":
            params["severity"] = severity
        rows = client.get("/incidents", params=params)
        return [[r["id"], r["inference_id"], r["severity"], r["status"],
                 (r.get("description") or "")[:80]] for r in rows]
    except Exception as e:
        return [[f"Error: {e}", "", "", "", ""]]


def update_incident(incident_id, status, description):
    try:
        client.patch(f"/incidents/{int(incident_id)}", json={"status": status, "description": description or None})
        return "Incidencia actualizada", list_incidents("todas", "todas")
    except Exception as e:
        return f"Error: {e}", list_incidents("todas", "todas")


# ---------- Construccion de la UI ----------
with gr.Blocks(title="AgroVision - Monitoreo foliar") as demo:
    gr.Markdown("# AgroVision\nSistema inteligente para agricultura: monitoreo y deteccion de enfermedades foliares.")

    with gr.Column(visible=True) as login_area:
        with gr.Tabs():
            with gr.Tab("Ingresar"):
                u = gr.Textbox(label="Usuario")
                p = gr.Textbox(label="Contrasena", type="password")
                btn_login = gr.Button("Iniciar sesion", variant="primary")
                msg_login = gr.Markdown()
            with gr.Tab("Registrarse"):
                r_u = gr.Textbox(label="Usuario")
                r_e = gr.Textbox(label="Correo")
                r_p = gr.Textbox(label="Contrasena", type="password")
                r_role = gr.Dropdown(["usuario", "operador", "admin"], value="usuario", label="Rol")
                btn_reg = gr.Button("Registrar")
                msg_reg = gr.Markdown()
                btn_reg.click(do_register, inputs=[r_u, r_e, r_p, r_role], outputs=msg_reg)

    with gr.Column(visible=False) as main_area:
        with gr.Row():
            gr.Markdown("## AgroVision")
            btn_logout = gr.Button(
                "🚪Cerrar sesión",
                variant="secondary",
                size="sm", 
                scale=0,
                min_width=110
            )

        with gr.Tabs():
            with gr.Tab("Fincas") as tab_fincas:
                n_name = gr.Textbox(label="Nombre")
                n_loc = gr.Textbox(label="Ubicacion")
                n_area = gr.Number(label="Area (ha)")
                btn_f = gr.Button("Crear finca")
                msg_f = gr.Markdown()
                tbl_f = gr.Dataframe(headers=["id", "nombre", "ubicacion", "area_ha"], interactive=False)
                btn_f.click(create_farm, inputs=[n_name, n_loc, n_area], outputs=[msg_f, tbl_f])
                tab_fincas.select(fn=list_farms, inputs=[], outputs=tbl_f)

            with gr.Tab("Lotes") as tab_lotes:
                l_farm = gr.Number(label="ID finca")
                l_name = gr.Textbox(label="Nombre lote")
                l_area = gr.Number(label="Area (m2)")
                l_desc = gr.Textbox(label="Descripcion")
                btn_l = gr.Button("Crear lote")
                msg_l = gr.Markdown()
                tbl_l = gr.Dataframe(headers=["id", "farm_id", "nombre", "area_m2"], interactive=False)
                btn_l.click(create_lot, inputs=[l_farm, l_name, l_area, l_desc], outputs=[msg_l, tbl_l])
                tab_lotes.select(fn=list_lots, inputs=[], outputs=tbl_l)

            with gr.Tab("Cultivos") as tab_cultivos:
                c_lot = gr.Number(label="ID lote")
                c_sp = gr.Textbox(label="Especie")
                c_var = gr.Textbox(label="Variedad")
                btn_c = gr.Button("Crear cultivo")
                msg_c = gr.Markdown()
                tbl_c = gr.Dataframe(headers=["id", "lot_id", "especie", "variedad"], interactive=False)
                btn_c.click(create_crop, inputs=[c_lot, c_sp, c_var], outputs=[msg_c, tbl_c])
                tab_cultivos.select(fn=list_crops, inputs=[], outputs=tbl_c)

            with gr.Tab("Analisis de imagen"):
                img_in = gr.Image(type="filepath", label="Subir imagen de hoja")
                crop_ref = gr.Number(label="ID cultivo (opcional)")
                btn_an = gr.Button("Analizar", variant="primary")
                resumen = gr.Textbox(label="Resumen de deteccion", lines=5)
                img_out = gr.Image(label="Imagen anotada")
                raw = gr.JSON(label="Detalle crudo")
                btn_an.click(analyze_image, inputs=[img_in, crop_ref], outputs=[resumen, img_out, raw])

            with gr.Tab("Historial") as tab_historial:
                tbl_h = gr.Dataframe(headers=["id", "img_id", "hojas", "sana", "mancha", "seca", "conf", "revisada"],
                                      interactive=False)
                btn_h = gr.Button("Actualizar historial")
                btn_h.click(list_inferences, outputs=tbl_h)
                with gr.Row():
                    r_id = gr.Number(label="ID inferencia")
                    r_rev = gr.Checkbox(label="Revisada", value=True)
                    r_notes = gr.Textbox(label="Notas del experto")
                btn_r = gr.Button("Marcar revision")
                msg_r = gr.Markdown()
                btn_r.click(review_inference, inputs=[r_id, r_rev, r_notes], outputs=[msg_r, tbl_h])
                tab_historial.select(fn=list_inferences, inputs=[], outputs=tbl_h)

            with gr.Tab("Incidencias") as tab_incidencias:
                st = gr.Dropdown(["todas", "abierta", "en_revision", "cerrada"], value="todas", label="Estado")
                sev = gr.Dropdown(["todas", "baja", "media", "alta"], value="todas", label="Severidad")
                btn_li = gr.Button("Listar")
                tbl_i = gr.Dataframe(headers=["id", "inf_id", "severidad", "estado", "descripcion"],
                                     interactive=False)
                btn_li.click(list_incidents, inputs=[st, sev], outputs=tbl_i)
                with gr.Row():
                    i_id = gr.Number(label="ID incidencia")
                    i_st = gr.Dropdown(["abierta", "en_revision", "cerrada"], value="en_revision", label="Nuevo estado")
                    i_desc = gr.Textbox(label="Comentario")
                btn_ui = gr.Button("Actualizar")
                msg_i = gr.Markdown()
                btn_ui.click(update_incident, inputs=[i_id, i_st, i_desc], outputs=[msg_i, tbl_i])
                tab_incidencias.select(fn=list_incidents, inputs=[st, sev], outputs=tbl_i)

    btn_login.click(
    fn=do_login,
    inputs=[u, p],
    outputs=[msg_login, login_area, main_area]
).then(
    fn=list_farms,
    inputs=[],
    outputs=tbl_f
).then(
    fn=list_lots,
    inputs=[],
    outputs=tbl_l
).then(
    fn=list_crops,
    inputs=[],
    outputs=tbl_c
).then(
    fn=list_inferences,
    inputs=[],
    outputs=tbl_h
).then(
    fn=list_incidents,
    inputs=[st, sev],
    outputs=tbl_i
)

    btn_logout.click(
        fn=do_logout,
        inputs=[],
        outputs=[login_area, main_area, msg_login]
    )

def launch():
    demo.launch(server_name="0.0.0.0", server_port=settings.gradio_port, show_error=True)


if __name__ == "__main__":
    launch()
