# Equidad y cumplimiento

Los criterios exactos dependen de la jurisdicción y del regulador. Este archivo fija los chequeos mínimos; la interpretación legal la valida el área de cumplimiento.

## Variables sensibles

No usar como variables del modelo atributos protegidos o que la normativa local prohíba para decisiones de crédito. Según el país suelen incluir: género, origen étnico, nacionalidad, religión, estado civil, discapacidad, orientación sexual, afiliación política o sindical. Verificar la lista vigente para el país del proyecto.

## Proxies

Excluir la variable sensible no alcanza: otras variables pueden reconstruirla.

- Revisar variables geográficas finas (código postal, barrio), nombre, tipo de dispositivo, horario de solicitud y patrones de consumo.
- Si se dispone de la variable sensible para auditoría, medir cuánto la predicen las variables del modelo.

## Métricas de auditoría

Si existe la variable sensible (solo para medir, no para entrenar), reportar por grupo:

- Tasa de aprobación al corte elegido.
- Tasa de malos entre aprobados.
- AUC y calibración por grupo.

Diferencias grandes requieren explicación de negocio documentada o ajuste del modelo.

## Explicabilidad de decisiones

- Poder dar razones de rechazo individuales (*reason codes*): las variables que más empujaron el score hacia abajo para ese caso.
- Con regresión logística sobre WoE salen directamente de los puntos por variable; con GBM, de los valores SHAP.
- Las razones tienen que ser comprensibles para el solicitante ("historial de atrasos reciente"), no nombres de columnas.

## Gobierno del modelo

- Validación independiente antes de producción cuando la organización lo requiera.
- Inventario de modelos con dueño, versión, fecha de aprobación y próxima revisión.
- Registro de cambios con justificación.
