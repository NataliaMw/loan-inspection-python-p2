# Especificación funcional — Evaluador de elegibilidad de préstamos

**Sistema:** Evaluador de elegibilidad de préstamos para una cooperativa de ahorro y crédito.
**Versión:** 1.0
**Estado:** Aprobada por el área de negocio.

> Este documento es la **fuente de verdad** sobre el comportamiento esperado del sistema. Cuando
> el código y esta especificación discrepan, **la especificación tiene la razón** y el código
> tiene un defecto.

---

## 1. Registro de socios

El sistema permite crear registros de socios de la cooperativa con nombre e identificación.

- El nombre no puede estar vacío.
- La identificación no puede estar vacía.

## 2. Datos financieros

Cada socio puede tener múltiples atributos numéricos: ingreso (`income`), deuda (`debt`), saldo
de ahorros (`savings_balance`), antigüedad en meses (`tenure_months`), edad (`age`), pagos
atrasados (`late_payments`), dependientes (`dependents`).

- Todos los montos deben ser números **no negativos**.
- La edad debe ser un entero positivo.
- La antigüedad en meses debe ser un entero no negativo.

## 3. Razón deuda-ingreso (DTI)

El sistema calcula la razón DTI de cada socio como **deuda dividida entre ingreso**.

## 4. Decisión de elegibilidad

El sistema convierte la razón DTI y el perfil del socio en una decisión de elegibilidad.

**Es elegible si se cumplen TODAS estas condiciones:**

1. El estado del socio es **ACTIVO**.
2. La razón DTI está **por debajo** del umbral de política aplicable:
   - Empleado: **0.40**
   - Jubilado: **0.35**
   - Categoría residual (ni empleado ni jubilado): **0.45**
3. La edad está dentro de los límites (ver §7).
4. Se cumple el requisito de antigüedad **o** el de garante:
   - Antigüedad de **al menos 9 meses** (es decir, `tenure_months >= 9`), **o**
   - El socio presenta un garante (`has_guarantor`).

**No es elegible en cualquier otro caso**, y el sistema devuelve **uno o más** códigos de razón
de la siguiente lista:

| Código | Significado |
|---|---|
| `DTI_HIGH` | La razón DTI alcanza o supera el umbral |
| `AGE_LOW` | Edad por debajo del mínimo |
| `AGE_HIGH` | Edad por encima del máximo |
| `TENURE_LOW` | Antigüedad insuficiente y sin garante |
| `INCOME_MISSING` | Ingreso no proporcionado |
| `INCOME_NONPOSITIVE` | Ingreso menor o igual a cero |
| `DEBT_INVALID` | Deuda ausente o negativa |
| `AMOUNT_BELOW_MIN` | El monto calculado quedó por debajo del piso |
| `STATUS_INACTIVE` | El socio no está activo |

**Un socio con estado inactivo NUNCA es elegible**, independientemente de su perfil financiero.

**Normalización del estado:** el estado del socio llega desde un sistema externo y puede venir
con espacios alrededor (por ejemplo `" ACTIVE "`). El sistema debe **recortar los espacios** antes
de comparar. Un estado `" ACTIVE "` es un socio activo.

## 5. Monto del préstamo

El sistema calcula el monto máximo del préstamo a partir del ingreso, el tipo de empleo y el
historial de pagos atrasados.

- El monto respeta un **techo de 15 000 USD**.
- El monto respeta un **piso de 200 USD**.
- Si el monto calculado queda por debajo del piso, el socio se marca como **no elegible** con la
  razón `AMOUNT_BELOW_MIN`.

## 6. Tasa de interés

El sistema calcula la tasa de interés según el tipo de empleo.

**Tasa base:**

| Tipo | Tasa base |
|---|---|
| Empleado | 12% |
| Jubilado | 14% |
| Categoría residual | 18% |

**Ajustes al alza:**
- Antigüedad menor a 6 meses: **+4%**
- Pagos atrasados por encima de 2: **+3% por cada pago atrasado adicional** a partir del tercero
- Tres o más dependientes: **+1%**

**Ajuste a la baja:**
- Saldo de ahorros de al menos el **50% del ingreso**: **−1%**

**Pisos de tasa (obligatorios):**
- Empleado: la tasa final **nunca puede ser menor a 8%**
- Jubilado: la tasa final **nunca puede ser menor a 10%**

## 7. Manejo de entradas inválidas

El sistema debe validar que:

- El ingreso sea numérico y positivo.
- La deuda sea numérica y no negativa.
- La edad esté **entre 18 y 65 inclusive**, excepto que los jubilados pueden superar los 65.
- El nombre y la identificación no estén vacíos.

**Una entrada inválida no debe hacer caer el sistema.** En su lugar, el sistema devuelve el
código de razón correspondiente.

## 8. Clasificación de socios

El sistema clasifica a los socios en categorías A, B, C, D según ingreso y saldo de ahorros.

| Categoría | Condición |
|---|---|
| A | Ingreso > 2000 **y** ahorros > 5000 |
| B | Ingreso > 1200 **y** ahorros > 2000 |
| C | Ingreso > 600 **y** ahorros > 500 |
| D | Cualquier otro caso |

Se evalúa en orden: la primera condición que se cumple determina la categoría.

## 9. Trazabilidad de auditoría

Cada evaluación incrementa un contador de auditoría. El historial de evaluaciones registra
marca de tiempo, ingreso y deuda de cada llamada.

**El historial de una evaluación no debe contaminar el de otra.** Cada llamada al evaluador es
independiente: dos llamadas distintas con los mismos datos deben producir exactamente el mismo
resultado, sin importar cuántas evaluaciones se hayan hecho antes.
