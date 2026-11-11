"""Pruebas del bloque 7 (buzzer de falla, placa A). Se agregan a las de pruebas_r2.py SIN cambiarlas: import pruebas_buzzer as PB (usa PR.m)."""
import pruebas_r2 as PR

BLK = "BUZZER"
SIM = "prueba_buzzer"
FUENTE = "simulación LTspice (prueba_buzzer.cir) con buzzer SUPUESTO de 400 Ω (12.5 mA); el buzzer real: a medir"

PR.BLOQUES.append(BLK)
m = PR.m

PR.resist("m_r7", BLK, ["BZ.D", "K"], " Placa A: buzzer, 2N3904, 4.7 kΩ y diodo ya puestos. El buzzer es magnético: puede marcar poco al principio mientras el multímetro lo carga; espera a que se estabilice.")
m("m_bz_sin", BLK, "Colector del 2N3904 sin falla (buzzer en silencio)", ["BZ.Q", "C"], ["BZ.Q", "E"], "V DC",
  "El voltaje entre el colector y el emisor del 2N3904 del buzzer.", "Confirma que sin falla el transistor está apagado y el buzzer no suena.",
  "Fuente conectada. Cubierta cerrada y sin pulsar FALLA (F = 0). Buzzer en silencio.", "≈ 5 V (entre 4.8 y 5.1 V)",
  ["Cerca de 0 V y suena: F = 1 (revisa el pestillo, bloque 3) o la base está pegada a 5 V o a f sin la resistencia de 4.7 kΩ.", "Marca 0 V y no suena: el colector no llega al buzzer (revisa el cable entre las filas del colector y del buzzer) o el buzzer está al revés/abierto.", "Entre 1 y 4 V: el transistor conduce a medias; revisa que la base no toque otra fila."],
  FUENTE, tabla=[["Sin falla (F = 0)", "≈ 5 V"], ["Con falla guardada (F = 1)", "0.05 a 0.3 V (a medir)"]],
  valida=False, nova="buzzer real", sim=[(SIM, "vc_sin", 4.95, 5.05)])
m("m_bz_vb", BLK, "Base del 2N3904 del buzzer", ["BZ.Q", "B"], ["BZ.Q", "E"], "V DC",
  "El voltaje entre la base y el emisor del 2N3904 del buzzer.", "Confirma que f llega a la base por la resistencia de 4.7 kΩ y que el transistor conduce con falla.",
  "Fuente conectada. Mide sin falla y luego con falla guardada (pulsa FALLA y suelta).", "Ver tabla",
  ["Con falla marca 0 V: la resistencia de 4.7 kΩ no llega a f (revisa el cable de f) o la base está en otra fila.", "Con falla marca más de 0.9 V: la resistencia o el transistor están mal (¿patas E-B-C al revés?).", "Sin falla marca más de 0.1 V: f no baja a 0 V; revisa el pestillo."],
  FUENTE, tabla=[["Sin falla (F = 0)", "≈ 0 V (menos de 0.1 V)"], ["Con falla guardada (F = 1)", "0.65 a 0.85 V"]],
  valida=False, nova="buzzer real", sim=[(SIM, "vb_con", 0.68, 0.80), (SIM, "vb_sin", -0.01, 0.01)])
m("m_bz_rb", BLK, "Caída en la resistencia de base de 4.7 kΩ", ["BZ.Rb", "1"], ["BZ.Rb", "2"], "V DC",
  "El voltaje entre los dos extremos de la resistencia de 4.7 kΩ (la corriente de base es ese voltaje entre 4.7 kΩ).", "Da la corriente de base real: debe ser suficiente para saturar el transistor.",
  "Fuente conectada. Falla guardada (pulsa FALLA y suelta).", "2.9 a 4.2 V (corriente de base de 0.6 a 0.9 mA)",
  ["Casi 0 V: no pasa corriente por la base (transistor abierto o resistencia mal puesta).", "Menos de 2.9 V: f está débil; revisa que el LED rojo y el 74HC00 no estén sobrecargados.", "Calcula Ib = voltaje / 4700; para un buzzer de 12.5 mA con ganancia 100 basta 0.13 mA."],
  FUENTE, tabla=None, valida=False, nova="buzzer real", sim=[(SIM, "vrb_con", 3.5, 4.2), (SIM, "vrb_peor", 2.8, 3.1)])
m("m_bz_vbz", BLK, "5 V en el buzzer con falla", ["BZ.Z", "+"], ["BZ.Z", "-"], "V DC",
  "El voltaje que recibe el buzzer (entre sus dos patas).", "Confirma que, con falla, el buzzer recibe casi los 5 V completos y suena.",
  "Fuente conectada. Mide sin falla y con falla guardada.", "Ver tabla",
  ["Con falla marca poco (menos de 4.5 V): el transistor no satura; revisa la prueba de la base y la caída en 4.7 kΩ.", "Con falla marca 5 V y no suena: el buzzer está al revés (la pata + o la marcada va a 5 V) o está dañado: pruébalo directo a 5 V.", "Sin falla marca más de 0.3 V: hay fuga por el transistor; revisa que la base no toque otra fila."],
  FUENTE, tabla=[["Sin falla (F = 0)", "≈ 0 V (menos de 0.3 V)"], ["Con falla guardada (F = 1)", "≈ 4.9 V (4.5 a 5 V; a medir)"]],
  valida=False, nova="buzzer real", sim=[(SIM, "vbz_con", 4.85, 5.0), (SIM, "vbz_peor", 4.85, 5.0)])
m("m_bz_snd", BLK, "El buzzer suena con la falla y se apaga con RESET", {"txt": "no se mide con multímetro: se escucha"}, {"txt": "oído (y el LED rojo como referencia)"}, "oído",
  "Si el buzzer suena exactamente cuando enciende el LED rojo.", "Es la alarma acústica que pide el enunciado, ligada a la misma señal f del LED rojo.",
  "Fuente conectada. Cubierta cerrada y E en 1.", "Suena con falla guardada y se apaga con RESET (ver tabla)",
  ["Suena al encender sin pulsar nada: el reset automático no limpió F; revisa el pestillo (bloque 3).", "Suena al soltar FALLA y deja de sonar solo: el pestillo no guarda; revisa el bloque 3.", "No se apaga con RESET: suelta FALLA antes de pulsar RESET (con FALLA pulsada el RESET no limpia)."],
  "lógica del pestillo (simulada en 1_LTspice/resultado_logica.md); el sonido del buzzer real: a medir",
  tabla=[["Sin falla", "silencio, LED rojo apagado"], ["Pulso FALLA", "suena, LED rojo enciende, motor parado"], ["Suelto FALLA", "sigue sonando (falla guardada)"], ["RESET con FALLA suelta", "se apaga el buzzer y el LED rojo"]],
  valida=False, nova="buzzer real")
