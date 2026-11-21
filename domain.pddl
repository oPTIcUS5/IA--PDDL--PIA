; PIA de Inteligencia Artificial
; Dominio original: recuperacion de un portal universitario
; Planificacion clasica (STRIPS + tipos)

(define (domain recuperacion-portal)
  (:requirements :strips :typing)

  (:types servidor respaldo parche)

  (:predicates
    (alerta ?s - servidor)
    (en-red ?s - servidor)
    (diagnosticado ?s - servidor)
    (aislado ?s - servidor)
    (respaldo-disponible ?b - respaldo)
    (respaldo-compatible ?b - respaldo ?s - servidor)
    (respaldo-validado ?b - respaldo)
    (datos-restaurados ?s - servidor)
    (integridad-confirmada ?s - servidor)
    (parche-disponible ?p - parche)
    (parche-compatible ?p - parche ?s - servidor)
    (parche-instalado ?s - servidor)
    (pruebas-aprobadas ?s - servidor)
    (servicio-operativo ?s - servidor)
    (monitoreo-activo ?s - servidor)
    (caso-cerrado ?s - servidor)
  )

  (:action diagnosticar
    :parameters (?s - servidor)
    :precondition (and
      (alerta ?s)
      (en-red ?s)
    )
    :effect (and
      (diagnosticado ?s)
    )
  )

  (:action aislar
    :parameters (?s - servidor)
    :precondition (and
      (diagnosticado ?s)
      (en-red ?s)
    )
    :effect (and
      (aislado ?s)
      (not (en-red ?s))
      (not (servicio-operativo ?s))
    )
  )

  (:action validar-respaldo
    :parameters (?b - respaldo ?s - servidor)
    :precondition (and
      (aislado ?s)
      (respaldo-disponible ?b)
      (respaldo-compatible ?b ?s)
    )
    :effect (and
      (respaldo-validado ?b)
    )
  )

  (:action restaurar-datos
    :parameters (?b - respaldo ?s - servidor)
    :precondition (and
      (aislado ?s)
      (respaldo-validado ?b)
      (respaldo-compatible ?b ?s)
    )
    :effect (and
      (datos-restaurados ?s)
      (not (integridad-confirmada ?s))
      (not (pruebas-aprobadas ?s))
    )
  )

  (:action verificar-integridad
    :parameters (?s - servidor)
    :precondition (and
      (aislado ?s)
      (datos-restaurados ?s)
    )
    :effect (and
      (integridad-confirmada ?s)
    )
  )

  (:action instalar-parche
    :parameters (?p - parche ?s - servidor)
    :precondition (and
      (aislado ?s)
      (parche-disponible ?p)
      (parche-compatible ?p ?s)
    )
    :effect (and
      (parche-instalado ?s)
      (not (pruebas-aprobadas ?s))
    )
  )

  (:action ejecutar-pruebas
    :parameters (?s - servidor)
    :precondition (and
      (aislado ?s)
      (datos-restaurados ?s)
      (integridad-confirmada ?s)
      (parche-instalado ?s)
    )
    :effect (and
      (pruebas-aprobadas ?s)
    )
  )

  (:action reconectar
    :parameters (?s - servidor)
    :precondition (and
      (aislado ?s)
      (pruebas-aprobadas ?s)
    )
    :effect (and
      (en-red ?s)
      (not (aislado ?s))
    )
  )

  (:action levantar-servicio
    :parameters (?s - servidor)
    :precondition (and
      (en-red ?s)
      (pruebas-aprobadas ?s)
      (integridad-confirmada ?s)
      (parche-instalado ?s)
    )
    :effect (and
      (servicio-operativo ?s)
    )
  )

  (:action activar-monitoreo
    :parameters (?s - servidor)
    :precondition (and
      (en-red ?s)
      (servicio-operativo ?s)
    )
    :effect (and
      (monitoreo-activo ?s)
    )
  )

  (:action cerrar-incidente
    :parameters (?s - servidor)
    :precondition (and
      (alerta ?s)
      (diagnosticado ?s)
      (servicio-operativo ?s)
      (monitoreo-activo ?s)
    )
    :effect (and
      (caso-cerrado ?s)
      (not (alerta ?s))
    )
  )
)
