; Problema concreto: recuperar el portal de inscripciones
; Hay dos respaldos y dos parches, pero solo uno de cada tipo es compatible.

(define (problem incidente-portal-inscripciones)
  (:domain recuperacion-portal)

  (:objects
    portal-inscripciones - servidor
    copia-noviembre copia-obsoleta - respaldo
    parche-estable parche-legacy - parche
  )

  (:init
    (alerta portal-inscripciones)
    (en-red portal-inscripciones)

    (respaldo-disponible copia-noviembre)
    (respaldo-disponible copia-obsoleta)
    (respaldo-compatible copia-noviembre portal-inscripciones)

    (parche-disponible parche-estable)
    (parche-disponible parche-legacy)
    (parche-compatible parche-estable portal-inscripciones)
  )

  (:goal
    (and
      (caso-cerrado portal-inscripciones)
      (servicio-operativo portal-inscripciones)
      (monitoreo-activo portal-inscripciones)
      (integridad-confirmada portal-inscripciones)
    )
  )
)
