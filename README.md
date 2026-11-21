# PIA de Inteligencia Artificial: recuperación segura de un portal universitario

**Tema:** planificación automatizada con PDDL  
**Tipo de planificación:** clásica, determinista, secuencial  
**Lenguaje:** PDDL con `:strips` y `:typing`  
**Integrante(s):** [Completar antes de entregar]  
**Materia y grupo:** [Completar antes de entregar]

## 1. Resumen del proyecto

Este proyecto modela la recuperación de un portal de inscripciones universitarias después de una alerta de seguridad. El servidor todavía está conectado a la red, pero su servicio no se considera operativo. El objetivo es recuperar los datos desde un respaldo compatible, aplicar un parche de seguridad, realizar verificaciones, volver a conectar el servidor y cerrar formalmente el incidente con el monitoreo activado.

La secuencia **no se programa manualmente en el dominio**: PDDL describe estados, condiciones y consecuencias de acciones. Un planificador determina una secuencia de acciones que cumple la meta. La solución calculada contiene **11 pasos**, por encima del mínimo de cinco.

Este es un modelo **abstracto**: los predicados representan hechos lógicos, no comandos que se ejecutan sobre servidores reales. Por ejemplo, `restaurar-datos` expresa una transición de estado; no restaura físicamente una base de datos.

## 2. Archivos

| Archivo | Contenido |
| --- | --- |
| `domain.pddl` | Tipos, 16 predicados, 11 acciones y sus precondiciones, efectos de agregación y eliminación. |
| `problem.pddl` | Objetos, estado inicial, restricciones de compatibilidad y meta. |
| `plan_ejemplo.txt` | Un plan de 11 pasos obtenido con búsqueda BFS independiente. |
| `verificar_plan.py` | Programa de apoyo que interpreta el subconjunto STRIPS utilizado, busca un plan mínimo y comprueba la meta. No requiere paquetes externos. |
| `README.md` | Documentación del proceso de diseño y explicación del modelo. |

## 3. Proceso de diseño

### 3.1. Identificar el escenario y el objetivo

El escenario elegido fue un **incidente en un portal de inscripciones**, en lugar de transportar objetos entre lugares o apilar bloques. Se fijó una meta verificable: un incidente puede considerarse cerrado solo cuando el servicio se encuentra operativo y monitorizado; adicionalmente, se exige la confirmación de integridad de los datos.

Se separo el escenario en cinco etapas funcionales:

1. **Contencion:** diagnosticar el incidente y aislar el equipo afectado.
2. **Recuperación:** elegir y validar un respaldo compatible, y restaurar los datos.
3. **Seguridad y calidad:** verificar la integridad, instalar un parche compatible y ejecutar pruebas.
4. **Reincorporación:** reconectar el servidor y reactivar el servicio.
5. **Seguimiento:** habilitar monitoreo y cerrar el incidente.

Se priorizaron dependencias que tienen sentido operativa: no se deben ejecutar pruebas completas antes de restaurar los datos, ni reconectar el servidor antes de aprobar esas pruebas.

### 3.2. Definir los tipos y los objetos

Se eligieron tres tipos: `servidor`, `respaldo` y `parche`.

- **Servidor:** `portal-inscripciones`.
- **Respaldos disponibles:** `copia-noviembre` y `copia-obsoleta`.
- **Parches disponibles:** `parche-estable` y `parche-legacy`.

En el estado inicial solo `copia-noviembre` y `parche-estable` se declaran compatibles con el servidor. Los otros dos objetos están disponibles, pero **no** son opciónes viables. Esto permite representar una seleccion basada en restricciones, y no solo una sucesión fija de acciones sin parámetros.

### 3.3. Elegir los predicados

Cada predicado representa un hecho booleano que puede estar presente o ausente en el estado del mundo. Se definieron los siguientes **16 predicados**:

| Predicado | Justificación |
| --- | --- |
| `(alerta ?s)` | Indica que existe un incidente abierto. |
| `(en-red ?s)` | Indica si el equipo se encuentra conectado. |
| `(diagnosticado ?s)` | Evita aislar sin haber identificado la alerta. |
| `(aislado ?s)` | Establece que el servidor está contenido. |
| `(respaldo-disponible ?b)` | Identifica respaldos utilizables. |
| `(respaldo-compatible ?b ?s)` | Excluye respaldos incompatibles con el servidor. |
| `(respaldo-validado ?b)` | Exige revisar el respaldo antes de usarlo. |
| `(datos-restaurados ?s)` | Señala que se aplicaron los datos recuperados. |
| `(integridad-confirmada ?s)` | Distingue restaurar de comprobar la integridad. |
| `(parche-disponible ?p)` | Identifica parches que se pueden instalar. |
| `(parche-compatible ?p ?s)` | Excluye parches incompatibles. |
| `(parche-instalado ?s)` | Registra que el servidor recibio la correccion. |
| `(pruebas-aprobadas ?s)` | Impide reconectar antes de probar el sistema. |
| `(servicio-operativo ?s)` | Representa la disponibilidad final del servicio. |
| `(monitoreo-activo ?s)` | Representa la observación posterior a la recuperación. |
| `(caso-cerrado ?s)` | Representa el cierre formal del incidente. |

**Supuesto de mundo cerrado:** en PDDL clásico, un hecho que no aparece en el estado inicial se considera falso. Por eso no se necesita escribir que `copia-obsoleta` es incompatible: simplemente no se declara `(respaldo-compatible copia-obsoleta portal-inscripciones)`.

### 3.4. Convertir las etapas en acciones

Se crearon **11 esquemas de acción**. Para cada uno se decidieron sus parámetros, precondiciones, hechos agregados (**Add**) y hechos eliminados (**Delete**). En la tabla, `s` indica servidor, `b` respaldo y `p` parche.

| Acción | Precondiciones relevantes | Add | Delete |
| --- | --- | --- | --- |
| `diagnosticar(s)` | Alerta, en red | Diagnosticado | — |
| `aislar(s)` | Diagnosticado, en red | Aislado | En red, servicio operativo |
| `validar-respaldo(b,s)` | Aislado, respaldo disponible y compatible | Respaldo validado | — |
| `restaurar-datos(b,s)` | Aislado, respaldo validado y compatible | Datos restaurados | Integridad confirmada, pruebas aprobadas |
| `verificar-integridad(s)` | Aislado, datos restaurados | Integridad confirmada | — |
| `instalar-parche(p,s)` | Aislado, parche disponible y compatible | Parche instalado | Pruebas aprobadas |
| `ejecutar-pruebas(s)` | Aislado, datos restaurados, integridad confirmada, parche instalado | Pruebas aprobadas | — |
| `reconectar(s)` | Aislado, pruebas aprobadas | En red | Aislado |
| `levantar-servicio(s)` | En red, pruebas aprobadas, integridad confirmada, parche instalado | Servicio operativo | — |
| `activar-monitoreo(s)` | En red, servicio operativo | Monitoreo activo | — |
| `cerrar-incidente(s)` | Alerta, diagnosticado, servicio operativo, monitoreo activo | Caso cerrado | Alerta |

**Importancia de los efectos Delete:** las acciones que solo registran un nuevo hecho tienen una lista Delete vacía; las acciones que modifican o invalidan un estado sí eliminan hechos previos. Por ejemplo, aislar elimina `(en-red ?s)`; reconectar elimina `(aislado ?s)`; restaurar datos e instalar un parche invalidan pruebas anteriores, si existieran. Esto evita que un estado antiguo sea tratado automáticamente como vigente. La acción final elimina la alerta, pues el incidente ha quedado cerrado.

### 3.5. Ajustes realizados para obtener el esquema final

- **Separar restauración y verificación.** Restaurar datos no equivale a comprobar que son íntegros; por eso son dos acciones distintas.
- **Separar parche y pruebas.** Un parche puede cambiar el comportamiento del sistema, por lo que `instalar-parche` elimina una aprobación de pruebas previa y `ejecutar-pruebas` requiere que el parche esté instalado.
- **Modelar el aislamiento como estado reversible.** `aislar` y `reconectar` agregan y eliminan hechos opuestos, evitando que el servidor quede simultáneamente aislado y conectado.
- **Introducir compatibilidad como criterio de selección.** Las relaciones `respaldo-compatible` y `parche-compatible` restringen los objetos utilizables.
- **Exigir monitoreo antes del cierre.** Recuperar el servicio no significa automáticamente haber cerrado el incidente: falta la supervisión posterior.

Estas decisiónes generan una **red de dependencias** y no una lista rigida de instrucciones. Por ejemplo, `instalar-parche` se puede hacer antes o después de `restaurar-datos`, siempre y cuando las pruebas se realicen al final de ambas tareas.

### 3.6. Originalidad frente a dominios conocidos

La inspiracion metodológica es la planificación clásica basada en **precondiciones y efectos**, como se estudia con ejemplos generales de STRIPS. Sin embargo, la problematica, los tipos, predicados y acciones se definieron específicamente para una recuperación informática universitaria:

- En **Blocks World**, se manipulan relaciones espaciales entre bloques, como colocarlos uno sobre otro. Aquí se controlan condiciones de aislamiento, integridad, compatibilidad y operatividad.
- En **Air Cargo**, se representa el transporte de cargas mediante aviones. Aqui no existe transporte de objetos: los cambios son transiciones logicas del ciclo de respuesta a un incidente.
- Una particularidad de este dominio es que **modificar datos o software invalida las pruebas previas**, lo cual obliga a comprobar de nuevo el sistema antes de reconectarlo.
- La existencia de respaldos y parches disponibles pero incompatibles introduce opciónes que el planificador debe descartar.

El modelo no es una copia con nombres cambiados de alguno de esos dominios; sus restricciones se construyeron a partir del escenario de recuperación definido en este proyecto.

## 4. Estado inicial y meta

### Estado inicial

- El servidor `portal-inscripciones` presenta una alerta y está conectado a la red.
- Dos respaldos están disponibles, pero **solo** `copia-noviembre` es compatible.
- Dos parches están disponibles, pero **solo** `parche-estable` es compatible.
- No se han realizado el diagnóstico, aislamiento, restauracion, verificaciones, pruebas, reactivacion o cierre.

### Meta

La conjuncion de los siguientes hechos:

```pddl
(and
  (caso-cerrado portal-inscripciones)
  (servicio-operativo portal-inscripciones)
  (monitoreo-activo portal-inscripciones)
  (integridad-confirmada portal-inscripciones)
)
```

Un solo paso no puede satisfacer la meta: cerrar el incidente exige monitoreo; el monitoreo exige un servicio operativo; la reactivacion exige pruebas aprobadas; y las pruebas exigen restauracion, integridad y parche, que a su vez requieren aislamiento y diagnóstico.

## 5. Plan encontrado y explicación acción por acción

Se verificó un plan mediante **búsqueda BFS** con un programa local que analiza los archivos PDDL. La búsqueda exploro los estados alcanzables del modelo y encontro un **plan mínimo de 11 acciones**. El planificador web podría producir otro orden igualmente válido.

| Paso | Acción | Por qué se puede ejecutar y que consigue |
| ---: | --- | --- |
| 1 | `diagnosticar portal-inscripciones` | Existe `alerta` y el servidor está `en-red`. Agrega `diagnosticado`. |
| 2 | `aislar portal-inscripciones` | Ya está diagnosticado y en red. Agrega `aislado`, elimina `en-red` y `servicio-operativo`. |
| 3 | `validar-respaldo copia-noviembre portal-inscripciones` | El servidor está aislado y el respaldo está disponible y es compatible. Agrega `respaldo-validado`. |
| 4 | `restaurar-datos copia-noviembre portal-inscripciones` | El respaldo compatible está validado y el servidor aislado. Agrega `datos-restaurados` y descarta verificaciones/pruebas antiguas. |
| 5 | `verificar-integridad portal-inscripciones` | Los datos ya fueron restaurados y el servidor sigue aislado. Agrega `integridad-confirmada`. |
| 6 | `instalar-parche parche-estable portal-inscripciones` | Hay un parche disponible y compatible y el servidor sigue aislado. Agrega `parche-instalado`, invalida pruebas anteriores. |
| 7 | `ejecutar-pruebas portal-inscripciones` | Se tienen datos restaurados, integridad confirmada, parche instalado y aislamiento. Agrega `pruebas-aprobadas`. |
| 8 | `reconectar portal-inscripciones` | El servidor permanece aislado y ya aprobó pruebas. Agrega `en-red` y elimina `aislado`. |
| 9 | `levantar-servicio portal-inscripciones` | Está en red, aprobó pruebas, tiene integridad confirmada y parche instalado. Agrega `servicio-operativo`. |
| 10 | `activar-monitoreo portal-inscripciones` | El servicio está operativo y en red. Agrega `monitoreo-activo`. |
| 11 | `cerrar-incidente portal-inscripciones` | Se conserva el diagnóstico, existe la alerta y el servicio y monitoreo están activos. Agrega `caso-cerrado` y elimina `alerta`. |

Al terminar están verdaderas las cuatro metas simultáneamente. La alerta ya no está activa y el servidor ha dejado de estar aislado.

### Por qué son necesarios 11 pasos como mínimo

Cada una de las once acciones introduce por primera vez un hecho causal necesario que no está en el estado inicial, desde `diagnosticado` hasta `caso-cerrado`. Ninguna acción de este dominio agrega simultáneamente dos de esos hitos necesarios. Por ello, no puede existir una solución con menos de once acciones. BFS confirma que el plan encontrado alcanza ese mínimo en el modelo formulado.

## 6. Pruebas y verificación

### Prueba local sin instalar nada

Desde la carpeta del proyecto, ejecutar:

```bash
python verificar_plan.py
```

El programa analiza ambos archivos, instancia las acciones, aplica una búsqueda en anchura (BFS) y válida cada transición del plan hallado. La salida comprobada para este problema incluye:

```text
Dominio: recuperacion-portal
Predicados: 16
Esquemas de accion: 11
Longitud mínima del plan (BFS): 11 acciones

META SATISFECHA:
  (caso-cerrado portal-inscripciones)
  (integridad-confirmada portal-inscripciones)
  (monitoreo-activo portal-inscripciones)
  (servicio-operativo portal-inscripciones)
```

El verificador incluido admite el subconjunto positivo de STRIPS y tipos usados **en estos archivos**; no pretende sustituir a un validador general de todas las variantes de PDDL.

### Ejecución con el editor PDDL

1. Abrir <https://editor.planning.domains/>.
2. Cargar `domain.pddl` y `problem.pddl` como archivos separados (opción **File > Load** o equivalente).
3. Elegir la opción **Solve** o **Plan** de la barra de herramientas.
4. Seleccionar como dominio `domain.pddl` y como problema `problem.pddl`.
5. Ejecutar el planificador y comprobar que se obtiene un plan. Puede haber diferencias en el orden de acciones independientes.
6. Mostrar en el video el código del dominio, las condiciones del problema, el resultado del planificador y la justificación de cada paso.

**Importante:** el plan ya fue verificado mediante BFS local; la ejecución concreta en el sitio externo debe realizarse en el navegador para capturar evidencia visual y comprobar la compatibilidad con el planificador elegido.

## 7. Alcances y limitaciones

La modelacion es intencionalmente simbólica. No incorpora duraciónes, costos, probabilidades de falla, multiples servidores simultaneos ni ejecución concurrente. Tampoco verifica de verdad la seguridad de un respaldo o la correccion de un parche: estas son propiedades asumidas como hechos del problema. Incorporar restricciones temporales y recursos seria una extension futura.

## 8. Referencia de la herramienta

- **PDDL Editor:** <https://editor.planning.domains/>. Entorno sugerido para editar y ejecutar problemas PDDL.
- **PDDL Solver:** <https://solver.planning.domains/>. Servicio de planificación automatizada de Planning.Domains.
