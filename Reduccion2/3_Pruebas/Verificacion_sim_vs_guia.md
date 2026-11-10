# Verificación: guía de pruebas contra LTspice

Las pruebas que citan una simulación se comparan con los .log actuales. Lo marcado *a medir* no tiene simulación.

| Prueba | Simulación | Valor simulado | Rango de la guía | Resultado |
|---|---|---|---|---|
| m_vb | prueba_sensor_ir · vb_sin | 0.8446 | 0.8 a 0.9 | OK |
| m_vb | prueba_sensor_ir · vb_con | 1.161 | 1.1 a 1.2 | OK |
| m_vc | prueba_sensor_ir · vc_sin | 4.166 | 4.1 a 4.25 | OK |
| m_vc | prueba_sensor_ir · vc_con | 2.855 | 2.8 a 2.95 | OK |
| m_vth | prueba_sensor_ir · vth | 3.302 | 3.2 a 3.4 | OK |
| m_p | prueba_sensor_ir · p_sin_objeto | 0.03071 | 0 a 0.1 | OK |
| m_p | prueba_sensor_ir · p_con_objeto | 4.935 | 4.8 a 5 | OK |
| m_setn | prueba_logica · setn_l1_falla_pulsada | 5e-05 | 0 a 0.1 | OK |
| m_setn | prueba_logica · setn_l3_falla_suelta_sin_reset | 5 | 4.9 a 5.1 | OK |
| m_fn | prueba_logica · fn_l1_falla_pulsada | 0 | 0 a 0.1 | OK |
| m_fn | prueba_logica · fn_l4_reset_con_falla_suelta | 5 | 4.9 a 5.1 | OK |
| m_led | prueba_logica · lo_a_111 | 2.004 | 1.9 a 2.1 | OK |
| m_led | prueba_logica · lo_a_110 | 5 | 4.9 a 5.05 | OK |
| m_gate | prueba_potencia_Rs15_bjt · vgate_on | 5 | 4.9 a 5.1 | OK |
| m_qb | prueba_potencia_Rs15_bjt · vbe_normal | 0.8862 | 0.7 a 0.95 | OK |
| m_qb | prueba_potencia_Rs15_bjt · vbe_lento | -0.003695 | -0.05 a 0.05 | OK |
| m_dm | prueba_potencia_Rs15_bjt · vdm_parado | 5 | 4.9 a 5.1 | OK |
| m_dm | prueba_potencia_Rs15_bjt · vce_normal | 0.09602 | 0.08 a 0.12 | OK |
| m_rs | prueba_potencia_Rs15_bjt · vrs_lento | 1.857 | 1.7 a 2 | OK |
| lógica (16 combinaciones + pestillo + LED) | prueba_logica | ver resultado_logica.md | 0 errores | OK |
| E y G limpios (U11) | prueba_logica | 16 combinaciones | = lo aplicado | OK |
| RST limpio (U11) | prueba_logica | 5.00 V pulsado / 0.005 V suelto | 5 V / 0 V | OK |

Comprobaciones fuera de rango: 0
