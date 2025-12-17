#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Inicialización: Tipos de Trabajo
Crea los tipos de trabajo predeterminados para el sistema de inversiones mecánicas

Uso:
    python crear_tipos_trabajo.py
"""

import sys
from app import db, create_app
from app.models import TipoTrabajo, Usuario
from datetime import datetime


def inicializar_tipos_trabajo():
    """Crea los tipos de trabajo predeterminados si no existen"""
    
    print("=" * 60)
    print("🔧 INICIALIZADOR DE TIPOS DE TRABAJO")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        # Obtener un usuario admin para el registro
        admin = Usuario.query.filter_by(rol='admin').first()
        
        if not admin:
            print("❌ ERROR: No se encontró un usuario administrador")
            print("   Crea un usuario con rol 'admin' primero")
            sys.exit(1)
        
        print(f"✅ Usuario administrador encontrado: {admin.username}")
        print()
        
        tipos = [
            {
                'nombre': 'Reparación Mecánica',
                'descripcion': 'Reparación general del sistema mecánico',
                'icono': '🔧'
            },
            {
                'nombre': 'Cambio de Pieza',
                'descripcion': 'Sustitución de piezas dañadas o desgastadas',
                'icono': '⚙️'
            },
            {
                'nombre': 'Mantenimiento',
                'descripcion': 'Mantenimiento preventivo o correctivo',
                'icono': '🛠️'
            },
            {
                'nombre': 'Cambio de Aceite',
                'descripcion': 'Cambio de aceite y filtros',
                'icono': '🛢️'
            },
            {
                'nombre': 'Frenos',
                'descripcion': 'Reparación o cambio del sistema de frenos',
                'icono': '🚙'
            },
            {
                'nombre': 'Motor',
                'descripcion': 'Reparación o ajuste del motor',
                'icono': '⚡'
            },
            {
                'nombre': 'Transmisión',
                'descripcion': 'Reparación del sistema de transmisión',
                'icono': '⚙️'
            },
            {
                'nombre': 'Suspensión',
                'descripcion': 'Reparación del sistema de suspensión',
                'icono': '🔩'
            },
            {
                'nombre': 'Eléctrico',
                'descripcion': 'Reparación del sistema eléctrico',
                'icono': '💡'
            },
            {
                'nombre': 'Carrocería',
                'descripcion': 'Reparación de la carrocería',
                'icono': '🚗'
            },
            {
                'nombre': 'Pintura',
                'descripcion': 'Trabajos de pintura',
                'icono': '🎨'
            },
            {
                'nombre': 'Otro',
                'descripcion': 'Otros trabajos no especificados',
                'icono': '📋'
            },
        ]
        
        print("🔍 Verificando tipos de trabajo existentes...")
        print()
        
        creados = 0
        existentes = 0
        
        for tipo_data in tipos:
            # Verificar si ya existe
            existe = TipoTrabajo.query.filter_by(nombre=tipo_data['nombre']).first()
            
            if not existe:
                tipo = TipoTrabajo(
                    nombre=tipo_data['nombre'],
                    descripcion=tipo_data['descripcion'],
                    usuario_registro_id=admin.id,
                    usuario_actualizo_id=admin.id
                )
                db.session.add(tipo)
                creados += 1
                print(f"   {tipo_data['icono']} ✅ CREADO: {tipo_data['nombre']}")
            else:
                existentes += 1
                print(f"   {tipo_data['icono']} ⏭️  YA EXISTE: {tipo_data['nombre']}")
        
        if creados > 0:
            try:
                db.session.commit()
                print()
                print("=" * 60)
                print(f"✅ ÉXITO: {creados} tipos de trabajo creados")
                print(f"ℹ️  INFO: {existentes} ya existían")
                print("=" * 60)
            except Exception as e:
                db.session.rollback()
                print()
                print("=" * 60)
                print(f"❌ ERROR al guardar en base de datos:")
                print(f"   {str(e)}")
                print("=" * 60)
                sys.exit(1)
        else:
            print()
            print("=" * 60)
            print("ℹ️  INFO: Todos los tipos de trabajo ya existían")
            print("=" * 60)
        
        print()
        print("📊 Resumen de Tipos de Trabajo:")
        print()
        
        total = TipoTrabajo.query.count()
        print(f"   Total registrados: {total}")
        print()
        
        # Mostrar todos los tipos
        todos = TipoTrabajo.query.all()
        for idx, tipo in enumerate(todos, 1):
            print(f"   {idx}. {tipo.nombre}")
        
        print()
        print("✅ Proceso completado exitosamente")


def verificar_base_datos():
    """Verifica que la tabla tipos_trabajos exista"""
    
    app = create_app()
    
    with app.app_context():
        try:
            count = TipoTrabajo.query.count()
            return True
        except Exception as e:
            print("❌ ERROR: La tabla 'tipos_trabajos' no existe")
            print(f"   {str(e)}")
            print()
            print("💡 SOLUCIÓN:")
            print("   1. Ejecuta las migraciones de Flask:")
            print("      flask db upgrade")
            print()
            print("   2. O crea la tabla manualmente:")
            print("      Revisa el archivo models.py")
            return False


if __name__ == '__main__':
    print()
    print("🚀 Iniciando script...")
    print()
    
    # Verificar base de datos
    if not verificar_base_datos():
        sys.exit(1)
    
    # Inicializar tipos de trabajo
    try:
        inicializar_tipos_trabajo()
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR CRÍTICO:")
        print(f"   {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("👋 Script finalizado")
    print()