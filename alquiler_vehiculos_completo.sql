-- ================================================================================
-- BASE DE DATOS COMPLETA: ALQUILER DE VEHÍCULOS
-- Incluye: Schema, Tablas Históricas, Triggers y Datos Iniciales
-- ================================================================================

-- Crear la base de datos
DROP DATABASE IF EXISTS alquiler_vehiculos;
CREATE DATABASE alquiler_vehiculos;
USE alquiler_vehiculos;

-- ================================================================================
-- SECCIÓN 1: TABLAS PRINCIPALES
-- ================================================================================

-- Tabla de Usuarios
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'user') NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);

-- Registro de Acceso
CREATE TABLE registro_acceso (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accion VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    detalles TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Catálogo: Marca y Modelo de Vehículos
CREATE TABLE vehiculo_marca_modelo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    logo_path VARCHAR(255) DEFAULT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Catálogo: Estados de Alquiler
CREATE TABLE estados_alquiler (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Catálogo: Métodos de Pago
CREATE TABLE metodos_pago (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Catálogo: Tipo de Cuentas
CREATE TABLE tipo_cuentas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tipo_cuenta VARCHAR(20) UNIQUE NOT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Catálogo: Bancos
CREATE TABLE bancos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    banco VARCHAR(50) NOT NULL,
    cuenta VARCHAR(30) UNIQUE NOT NULL,
    tipo_cuenta_id INT NOT NULL,
    cedula VARCHAR(20) NOT NULL,
    administrador VARCHAR(100) NOT NULL,
    logo_path VARCHAR(255) DEFAULT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_cuenta_id) REFERENCES tipo_cuentas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Catálogo: Parentescos
CREATE TABLE parentescos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parentesco VARCHAR(50) UNIQUE NOT NULL,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Propietarios
CREATE TABLE propietarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT,
    nombre_apellido VARCHAR(255) NOT NULL,
    documento_buena_conducta_path VARCHAR(255) DEFAULT NULL,
    cedula VARCHAR(255) UNIQUE,
    cedula_path VARCHAR(255) DEFAULT NULL,
    licencia VARCHAR(255) UNIQUE,
    licencia_path VARCHAR(255) DEFAULT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(255),
    email VARCHAR(255),
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Referencias de Propietarios
CREATE TABLE referencias_propietarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    propietario_id INT NOT NULL,
    nombre_apellido VARCHAR(100) NOT NULL,
    parentesco_id INT NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (propietario_id) REFERENCES propietarios(id) ON DELETE CASCADE,
    FOREIGN KEY (parentesco_id) REFERENCES parentescos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Inquilinos
CREATE TABLE inquilinos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_apellido VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    documento_buena_conducta_path VARCHAR(255) DEFAULT NULL,
    cedula VARCHAR(20) UNIQUE,
    cedula_path VARCHAR(255) DEFAULT NULL,
    licencia VARCHAR(50) UNIQUE,
    licencia_path VARCHAR(255) DEFAULT NULL,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Garantes de Inquilinos
CREATE TABLE garantes_inquilinos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    inquilino_id INT NOT NULL,
    nombre_apellido VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    parentesco_id INT NOT NULL,
    documento_referencia_laboral_path VARCHAR(255) DEFAULT NULL,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id) ON DELETE CASCADE,
    FOREIGN KEY (parentesco_id) REFERENCES parentescos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Referencias de Inquilinos
CREATE TABLE referencias_inquilinos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    inquilino_id INT NOT NULL,
    nombre_apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    parentesco_id INT NOT NULL,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id) ON DELETE CASCADE,
    FOREIGN KEY (parentesco_id) REFERENCES parentescos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Vehículos
CREATE TABLE vehiculos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    propietario_id INT NOT NULL,
    placa VARCHAR(20) UNIQUE NOT NULL,
    marca_modelo_vehiculo_id INT NOT NULL,
    ano YEAR,
    color VARCHAR(30),
    descripcion TEXT,
    precio_semanal DECIMAL(10,2) NOT NULL,
    condiciones TEXT,
    disponible BOOLEAN DEFAULT TRUE,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (marca_modelo_vehiculo_id) REFERENCES vehiculo_marca_modelo(id) ON DELETE RESTRICT,
    FOREIGN KEY (propietario_id) REFERENCES propietarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Mecánicos
CREATE TABLE mecanicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    especialidad VARCHAR(100),
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tipos de Trabajos
CREATE TABLE tipos_trabajos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Trabajos en Vehículos
CREATE TABLE trabajos_vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    mecanico_id INT NOT NULL,
    tipo_trabajo_id INT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    descripcion TEXT NOT NULL,
    costo DECIMAL(10,2) DEFAULT 0.00,
    estado ENUM('pendiente', 'en_progreso', 'completado', 'cancelado') DEFAULT 'pendiente',
    notas TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE,
    FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id) ON DELETE RESTRICT,
    FOREIGN KEY (tipo_trabajo_id) REFERENCES tipos_trabajos(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Piezas
CREATE TABLE piezas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50),
    estado ENUM('nueva', 'usada') NOT NULL,
    costo DECIMAL(10,2) NOT NULL,
    descripcion TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Piezas Usadas
CREATE TABLE piezas_usadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trabajo_id INT NOT NULL,
    pieza_id INT NOT NULL,
    cantidad INT DEFAULT 1,
    costo_unitario DECIMAL(10,2) NOT NULL,
    notas TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trabajo_id) REFERENCES trabajos_vehiculos(id) ON DELETE CASCADE,
    FOREIGN KEY (pieza_id) REFERENCES piezas(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Alquileres
CREATE TABLE alquileres (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehiculo_id INT NOT NULL,
    inquilino_id INT NOT NULL,
    estado_id INT NOT NULL,
    fecha_alquiler_inicio DATE NOT NULL,
    fecha_alquiler_fin DATE NOT NULL,
    semana INT NOT NULL,
    dia_trabajo INT,
    ingreso DECIMAL(10,2) NOT NULL,
    monto_descuento DECIMAL(10,2) DEFAULT 0.00,
    concepto_descuento TEXT,
    notas TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE,
    FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id) ON DELETE CASCADE,
    FOREIGN KEY (estado_id) REFERENCES estados_alquiler(id) ON DELETE RESTRICT
);

-- Deudas
CREATE TABLE deudas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehiculo_id INT NOT NULL,
    inquilino_id INT NOT NULL,
    alquiler_id INT NOT NULL,
    monto_deuda DECIMAL(10,2) NOT NULL,
    dias_retraso INT NOT NULL,
    penalizacion_diaria DECIMAL(10,2) DEFAULT 0.00,
    estado ENUM('pendiente', 'pagado', 'condonado') DEFAULT 'pendiente',
    fecha_vencimiento DATE NOT NULL,
    notas TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE,
    FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id) ON DELETE CASCADE,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id) ON DELETE CASCADE
);

-- Pagos
CREATE TABLE pagos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    alquiler_id INT NOT NULL,
    metodo_pago_id INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha_pago DATE NOT NULL,
    deducciones DECIMAL(10,2) DEFAULT 0.00,
    neto DECIMAL(10,2) NOT NULL,
    comprobante VARCHAR(100),
    notas TEXT,
    usuario_registro_id INT NOT NULL,
    fecha_hora_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_actualizo_id INT NOT NULL,
    fecha_hora_actualizo TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_actualizo_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id) ON DELETE CASCADE,
    FOREIGN KEY (metodo_pago_id) REFERENCES metodos_pago(id) ON DELETE RESTRICT
);

-- Índices
CREATE INDEX idx_alquileres_fecha_inicio ON alquileres(fecha_alquiler_inicio);
CREATE INDEX idx_alquileres_fecha_fin ON alquileres(fecha_alquiler_fin);
CREATE INDEX idx_pagos_fecha ON pagos(fecha_pago);
CREATE INDEX idx_vehiculos_placa ON vehiculos(placa);
CREATE INDEX idx_inquilinos_cedula ON inquilinos(cedula);
CREATE INDEX idx_propietarios_cedula ON propietarios(cedula);

-- ================================================================================
-- SECCIÓN 2: TABLAS DE HISTÓRICO
-- ================================================================================

-- Histórico de Usuarios
CREATE TABLE historico_usuarios (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    username VARCHAR(50),
    password VARCHAR(255),
    rol ENUM('admin', 'user'),
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(100),
    telefono VARCHAR(20),
    fecha_creacion TIMESTAMP,
    activo BOOLEAN
);

-- Histórico de Vehículo Marca Modelo
CREATE TABLE historico_vehiculo_marca_modelo (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    tipo VARCHAR(20),
    logo_path VARCHAR(255),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Estados Alquiler
CREATE TABLE historico_estados_alquiler (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    nombre VARCHAR(50),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Métodos de Pago
CREATE TABLE historico_metodos_pago (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    nombre VARCHAR(50),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Tipo Cuentas
CREATE TABLE historico_tipo_cuentas (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    tipo_cuenta VARCHAR(20),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Bancos
CREATE TABLE historico_bancos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    banco VARCHAR(50),
    cuenta VARCHAR(30),
    tipo_cuenta_id INT,
    cedula VARCHAR(20),
    administrador VARCHAR(100),
    logo_path VARCHAR(255),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Parentescos
CREATE TABLE historico_parentescos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    parentesco VARCHAR(50),
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Propietarios
CREATE TABLE historico_propietarios (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    usuario_id INT,
    nombre_apellido VARCHAR(100),
    documento_buena_conducta_path VARCHAR(255),
    cedula VARCHAR(20),
    cedula_path VARCHAR(255),
    licencia VARCHAR(50),
    licencia_path VARCHAR(255),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Referencias Propietarios
CREATE TABLE historico_referencias_propietarios (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    propietario_id INT,
    nombre_apellido VARCHAR(100),
    parentesco_id INT,
    telefono VARCHAR(20),
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Inquilinos
CREATE TABLE historico_inquilinos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    nombre_apellido VARCHAR(100),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    documento_buena_conducta_path VARCHAR(255),
    cedula VARCHAR(20),
    cedula_path VARCHAR(255),
    licencia VARCHAR(50),
    licencia_path VARCHAR(255),
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Garantes Inquilinos
CREATE TABLE historico_garantes_inquilinos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    inquilino_id INT,
    nombre_apellido VARCHAR(100),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    parentesco_id INT,
    documento_referencia_laboral_path VARCHAR(255),
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Referencias Inquilinos
CREATE TABLE historico_referencias_inquilinos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    inquilino_id INT,
    nombre_apellido VARCHAR(100),
    telefono VARCHAR(20),
    parentesco_id INT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Vehículos
CREATE TABLE historico_vehiculos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    propietario_id INT,
    placa VARCHAR(20),
    marca_modelo_vehiculo_id INT,
    ano YEAR,
    color VARCHAR(30),
    descripcion TEXT,
    precio_semanal DECIMAL(10,2),
    condiciones TEXT,
    disponible BOOLEAN,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Mecánicos
CREATE TABLE historico_mecanicos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    nombre VARCHAR(100),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    especialidad VARCHAR(100),
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP,
    activo BOOLEAN
);

-- Histórico de Tipos Trabajos
CREATE TABLE historico_tipos_trabajos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    nombre VARCHAR(100),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Trabajos Vehículos
CREATE TABLE historico_trabajos_vehiculos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    vehiculo_id INT,
    mecanico_id INT,
    tipo_trabajo_id INT,
    fecha_inicio DATE,
    fecha_fin DATE,
    descripcion TEXT,
    costo DECIMAL(10,2),
    estado ENUM('pendiente', 'en_progreso', 'completado', 'cancelado'),
    notas TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Piezas
CREATE TABLE historico_piezas (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    nombre VARCHAR(100),
    marca VARCHAR(50),
    modelo VARCHAR(50),
    estado ENUM('nueva', 'usada'),
    costo DECIMAL(10,2),
    descripcion TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Piezas Usadas
CREATE TABLE historico_piezas_usadas (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    trabajo_id INT,
    pieza_id INT,
    cantidad INT,
    costo_unitario DECIMAL(10,2),
    notas TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP
);

-- Histórico de Alquileres
CREATE TABLE historico_alquileres (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    vehiculo_id INT,
    inquilino_id INT,
    estado_id INT,
    fecha_alquiler_inicio DATE,
    fecha_alquiler_fin DATE,
    semana INT,
    dia_trabajo INT,
    ingreso DECIMAL(10,2),
    monto_descuento DECIMAL(10,2),
    concepto_descuento TEXT,
    notas TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Deudas
CREATE TABLE historico_deudas (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    vehiculo_id INT,
    inquilino_id INT,
    alquiler_id INT,
    monto_deuda DECIMAL(10,2),
    dias_retraso INT,
    penalizacion_diaria DECIMAL(10,2),
    estado ENUM('pendiente', 'pagado', 'condonado'),
    fecha_vencimiento DATE,
    notas TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- Histórico de Pagos
CREATE TABLE historico_pagos (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    tipo_operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    fecha_hora_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_operacion_id INT,
    id INT,
    alquiler_id INT,
    metodo_pago_id INT,
    monto DECIMAL(10,2),
    fecha_pago DATE,
    deducciones DECIMAL(10,2),
    neto DECIMAL(10,2),
    comprobante VARCHAR(100),
    notas TEXT,
    usuario_registro_id INT,
    fecha_hora_registro TIMESTAMP,
    usuario_actualizo_id INT,
    fecha_hora_actualizo TIMESTAMP
);

-- ================================================================================
-- SECCIÓN 3: TRIGGERS
-- ================================================================================

DELIMITER $$

-- TRIGGERS PARA USUARIOS
CREATE TRIGGER trg_usuarios_insert
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_usuarios (
        tipo_operacion, usuario_operacion_id,
        id, username, password, rol, nombre, apellido, email, telefono, fecha_creacion, activo
    ) VALUES (
        'INSERT', NEW.id,
        NEW.id, NEW.username, NEW.password, NEW.rol, NEW.nombre, NEW.apellido, NEW.email, NEW.telefono, NEW.fecha_creacion, NEW.activo
    );
END$$

CREATE TRIGGER trg_usuarios_update
AFTER UPDATE ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_usuarios (
        tipo_operacion, usuario_operacion_id,
        id, username, password, rol, nombre, apellido, email, telefono, fecha_creacion, activo
    ) VALUES (
        'UPDATE', NEW.id,
        NEW.id, NEW.username, NEW.password, NEW.rol, NEW.nombre, NEW.apellido, NEW.email, NEW.telefono, NEW.fecha_creacion, NEW.activo
    );
END$$

CREATE TRIGGER trg_usuarios_delete
BEFORE DELETE ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_usuarios (
        tipo_operacion, usuario_operacion_id,
        id, username, password, rol, nombre, apellido, email, telefono, fecha_creacion, activo
    ) VALUES (
        'DELETE', OLD.id,
        OLD.id, OLD.username, OLD.password, OLD.rol, OLD.nombre, OLD.apellido, OLD.email, OLD.telefono, OLD.fecha_creacion, OLD.activo
    );
END$$

-- TRIGGERS PARA VEHICULO_MARCA_MODELO
CREATE TRIGGER trg_vehiculo_marca_modelo_insert
AFTER INSERT ON vehiculo_marca_modelo
FOR EACH ROW
BEGIN
    INSERT INTO historico_vehiculo_marca_modelo (
        tipo_operacion, usuario_operacion_id,
        id, marca, modelo, tipo, logo_path, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.marca, NEW.modelo, NEW.tipo, NEW.logo_path, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_vehiculo_marca_modelo_update
AFTER UPDATE ON vehiculo_marca_modelo
FOR EACH ROW
BEGIN
    INSERT INTO historico_vehiculo_marca_modelo (
        tipo_operacion, usuario_operacion_id,
        id, marca, modelo, tipo, logo_path, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.marca, NEW.modelo, NEW.tipo, NEW.logo_path, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_vehiculo_marca_modelo_delete
BEFORE DELETE ON vehiculo_marca_modelo
FOR EACH ROW
BEGIN
    INSERT INTO historico_vehiculo_marca_modelo (
        tipo_operacion, usuario_operacion_id,
        id, marca, modelo, tipo, logo_path, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.marca, OLD.modelo, OLD.tipo, OLD.logo_path, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA ESTADOS_ALQUILER
CREATE TRIGGER trg_estados_alquiler_insert
AFTER INSERT ON estados_alquiler
FOR EACH ROW
BEGIN
    INSERT INTO historico_estados_alquiler (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.nombre, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_estados_alquiler_update
AFTER UPDATE ON estados_alquiler
FOR EACH ROW
BEGIN
    INSERT INTO historico_estados_alquiler (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.nombre, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_estados_alquiler_delete
BEFORE DELETE ON estados_alquiler
FOR EACH ROW
BEGIN
    INSERT INTO historico_estados_alquiler (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.nombre, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA METODOS_PAGO
CREATE TRIGGER trg_metodos_pago_insert
AFTER INSERT ON metodos_pago
FOR EACH ROW
BEGIN
    INSERT INTO historico_metodos_pago (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.nombre, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_metodos_pago_update
AFTER UPDATE ON metodos_pago
FOR EACH ROW
BEGIN
    INSERT INTO historico_metodos_pago (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.nombre, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_metodos_pago_delete
BEFORE DELETE ON metodos_pago
FOR EACH ROW
BEGIN
    INSERT INTO historico_metodos_pago (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.nombre, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA TIPO_CUENTAS
CREATE TRIGGER trg_tipo_cuentas_insert
AFTER INSERT ON tipo_cuentas
FOR EACH ROW
BEGIN
    INSERT INTO historico_tipo_cuentas (
        tipo_operacion, usuario_operacion_id,
        id, tipo_cuenta, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.tipo_cuenta, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_tipo_cuentas_update
AFTER UPDATE ON tipo_cuentas
FOR EACH ROW
BEGIN
    INSERT INTO historico_tipo_cuentas (
        tipo_operacion, usuario_operacion_id,
        id, tipo_cuenta, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.tipo_cuenta, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_tipo_cuentas_delete
BEFORE DELETE ON tipo_cuentas
FOR EACH ROW
BEGIN
    INSERT INTO historico_tipo_cuentas (
        tipo_operacion, usuario_operacion_id,
        id, tipo_cuenta, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.tipo_cuenta, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA BANCOS
CREATE TRIGGER trg_bancos_insert
AFTER INSERT ON bancos
FOR EACH ROW
BEGIN
    INSERT INTO historico_bancos (
        tipo_operacion, usuario_operacion_id,
        id, banco, cuenta, tipo_cuenta_id, cedula, administrador, logo_path, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.banco, NEW.cuenta, NEW.tipo_cuenta_id, NEW.cedula, NEW.administrador, NEW.logo_path, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_bancos_update
AFTER UPDATE ON bancos
FOR EACH ROW
BEGIN
    INSERT INTO historico_bancos (
        tipo_operacion, usuario_operacion_id,
        id, banco, cuenta, tipo_cuenta_id, cedula, administrador, logo_path, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.banco, NEW.cuenta, NEW.tipo_cuenta_id, NEW.cedula, NEW.administrador, NEW.logo_path, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_bancos_delete
BEFORE DELETE ON bancos
FOR EACH ROW
BEGIN
    INSERT INTO historico_bancos (
        tipo_operacion, usuario_operacion_id,
        id, banco, cuenta, tipo_cuenta_id, cedula, administrador, logo_path, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.banco, OLD.cuenta, OLD.tipo_cuenta_id, OLD.cedula, OLD.administrador, OLD.logo_path, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA PARENTESCOS
CREATE TRIGGER trg_parentescos_insert
AFTER INSERT ON parentescos
FOR EACH ROW
BEGIN
    INSERT INTO historico_parentescos (
        tipo_operacion, usuario_operacion_id,
        id, parentesco, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.parentesco, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_parentescos_update
AFTER UPDATE ON parentescos
FOR EACH ROW
BEGIN
    INSERT INTO historico_parentescos (
        tipo_operacion, usuario_operacion_id,
        id, parentesco, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.parentesco, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_parentescos_delete
BEFORE DELETE ON parentescos
FOR EACH ROW
BEGIN
    INSERT INTO historico_parentescos (
        tipo_operacion, usuario_operacion_id,
        id, parentesco, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.parentesco, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA PROPIETARIOS
CREATE TRIGGER trg_propietarios_insert
AFTER INSERT ON propietarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_propietarios (
        tipo_operacion, usuario_operacion_id,
        id, usuario_id, nombre_apellido, documento_buena_conducta_path, cedula, cedula_path, licencia, licencia_path, direccion, telefono, email, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.usuario_id, NEW.nombre_apellido, NEW.documento_buena_conducta_path, NEW.cedula, NEW.cedula_path, NEW.licencia, NEW.licencia_path, NEW.direccion, NEW.telefono, NEW.email, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_propietarios_update
AFTER UPDATE ON propietarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_propietarios (
        tipo_operacion, usuario_operacion_id,
        id, usuario_id, nombre_apellido, documento_buena_conducta_path, cedula, cedula_path, licencia, licencia_path, direccion, telefono, email, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.usuario_id, NEW.nombre_apellido, NEW.documento_buena_conducta_path, NEW.cedula, NEW.cedula_path, NEW.licencia, NEW.licencia_path, NEW.direccion, NEW.telefono, NEW.email, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_propietarios_delete
BEFORE DELETE ON propietarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_propietarios (
        tipo_operacion, usuario_operacion_id,
        id, usuario_id, nombre_apellido, documento_buena_conducta_path, cedula, cedula_path, licencia, licencia_path, direccion, telefono, email, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.usuario_id, OLD.nombre_apellido, OLD.documento_buena_conducta_path, OLD.cedula, OLD.cedula_path, OLD.licencia, OLD.licencia_path, OLD.direccion, OLD.telefono, OLD.email, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA REFERENCIAS_PROPIETARIOS
CREATE TRIGGER trg_referencias_propietarios_insert
AFTER INSERT ON referencias_propietarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_referencias_propietarios (
        tipo_operacion, usuario_operacion_id,
        id, propietario_id, nombre_apellido, parentesco_id, telefono, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.propietario_id, NEW.nombre_apellido, NEW.parentesco_id, NEW.telefono, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_referencias_propietarios_update
AFTER UPDATE ON referencias_propietarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_referencias_propietarios (
        tipo_operacion, usuario_operacion_id,
        id, propietario_id, nombre_apellido, parentesco_id, telefono, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.propietario_id, NEW.nombre_apellido, NEW.parentesco_id, NEW.telefono, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_referencias_propietarios_delete
BEFORE DELETE ON referencias_propietarios
FOR EACH ROW
BEGIN
    INSERT INTO historico_referencias_propietarios (
        tipo_operacion, usuario_operacion_id,
        id, propietario_id, nombre_apellido, parentesco_id, telefono, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.propietario_id, OLD.nombre_apellido, OLD.parentesco_id, OLD.telefono, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA INQUILINOS
CREATE TRIGGER trg_inquilinos_insert
AFTER INSERT ON inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, nombre_apellido, direccion, telefono, email, documento_buena_conducta_path, cedula, cedula_path, licencia, licencia_path, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.nombre_apellido, NEW.direccion, NEW.telefono, NEW.email, NEW.documento_buena_conducta_path, NEW.cedula, NEW.cedula_path, NEW.licencia, NEW.licencia_path, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_inquilinos_update
AFTER UPDATE ON inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, nombre_apellido, direccion, telefono, email, documento_buena_conducta_path, cedula, cedula_path, licencia, licencia_path, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.nombre_apellido, NEW.direccion, NEW.telefono, NEW.email, NEW.documento_buena_conducta_path, NEW.cedula, NEW.cedula_path, NEW.licencia, NEW.licencia_path, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_inquilinos_delete
BEFORE DELETE ON inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, nombre_apellido, direccion, telefono, email, documento_buena_conducta_path, cedula, cedula_path, licencia, licencia_path, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.nombre_apellido, OLD.direccion, OLD.telefono, OLD.email, OLD.documento_buena_conducta_path, OLD.cedula, OLD.cedula_path, OLD.licencia, OLD.licencia_path, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA GARANTES_INQUILINOS
CREATE TRIGGER trg_garantes_inquilinos_insert
AFTER INSERT ON garantes_inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_garantes_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, inquilino_id, nombre_apellido, direccion, telefono, email, parentesco_id, documento_referencia_laboral_path, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.inquilino_id, NEW.nombre_apellido, NEW.direccion, NEW.telefono, NEW.email, NEW.parentesco_id, NEW.documento_referencia_laboral_path, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_garantes_inquilinos_update
AFTER UPDATE ON garantes_inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_garantes_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, inquilino_id, nombre_apellido, direccion, telefono, email, parentesco_id, documento_referencia_laboral_path, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.inquilino_id, NEW.nombre_apellido, NEW.direccion, NEW.telefono, NEW.email, NEW.parentesco_id, NEW.documento_referencia_laboral_path, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_garantes_inquilinos_delete
BEFORE DELETE ON garantes_inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_garantes_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, inquilino_id, nombre_apellido, direccion, telefono, email, parentesco_id, documento_referencia_laboral_path, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.inquilino_id, OLD.nombre_apellido, OLD.direccion, OLD.telefono, OLD.email, OLD.parentesco_id, OLD.documento_referencia_laboral_path, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA REFERENCIAS_INQUILINOS
CREATE TRIGGER trg_referencias_inquilinos_insert
AFTER INSERT ON referencias_inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_referencias_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, inquilino_id, nombre_apellido, telefono, parentesco_id, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.inquilino_id, NEW.nombre_apellido, NEW.telefono, NEW.parentesco_id, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_referencias_inquilinos_update
AFTER UPDATE ON referencias_inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_referencias_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, inquilino_id, nombre_apellido, telefono, parentesco_id, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.inquilino_id, NEW.nombre_apellido, NEW.telefono, NEW.parentesco_id, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_referencias_inquilinos_delete
BEFORE DELETE ON referencias_inquilinos
FOR EACH ROW
BEGIN
    INSERT INTO historico_referencias_inquilinos (
        tipo_operacion, usuario_operacion_id,
        id, inquilino_id, nombre_apellido, telefono, parentesco_id, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.inquilino_id, OLD.nombre_apellido, OLD.telefono, OLD.parentesco_id, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA VEHICULOS
CREATE TRIGGER trg_vehiculos_insert
AFTER INSERT ON vehiculos
FOR EACH ROW
BEGIN
    INSERT INTO historico_vehiculos (
        tipo_operacion, usuario_operacion_id,
        id, propietario_id, placa, marca_modelo_vehiculo_id, ano, color, descripcion, precio_semanal, condiciones, disponible, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.propietario_id, NEW.placa, NEW.marca_modelo_vehiculo_id, NEW.ano, NEW.color, NEW.descripcion, NEW.precio_semanal, NEW.condiciones, NEW.disponible, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_vehiculos_update
AFTER UPDATE ON vehiculos
FOR EACH ROW
BEGIN
    INSERT INTO historico_vehiculos (
        tipo_operacion, usuario_operacion_id,
        id, propietario_id, placa, marca_modelo_vehiculo_id, ano, color, descripcion, precio_semanal, condiciones, disponible, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.propietario_id, NEW.placa, NEW.marca_modelo_vehiculo_id, NEW.ano, NEW.color, NEW.descripcion, NEW.precio_semanal, NEW.condiciones, NEW.disponible, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_vehiculos_delete
BEFORE DELETE ON vehiculos
FOR EACH ROW
BEGIN
    INSERT INTO historico_vehiculos (
        tipo_operacion, usuario_operacion_id,
        id, propietario_id, placa, marca_modelo_vehiculo_id, ano, color, descripcion, precio_semanal, condiciones, disponible, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.propietario_id, OLD.placa, OLD.marca_modelo_vehiculo_id, OLD.ano, OLD.color, OLD.descripcion, OLD.precio_semanal, OLD.condiciones, OLD.disponible, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA MECANICOS
CREATE TRIGGER trg_mecanicos_insert
AFTER INSERT ON mecanicos
FOR EACH ROW
BEGIN
    INSERT INTO historico_mecanicos (
        tipo_operacion, usuario_operacion_id,
        id, nombre, direccion, telefono, email, especialidad, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo, activo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.nombre, NEW.direccion, NEW.telefono, NEW.email, NEW.especialidad, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo, NEW.activo
    );
END$$

CREATE TRIGGER trg_mecanicos_update
AFTER UPDATE ON mecanicos
FOR EACH ROW
BEGIN
    INSERT INTO historico_mecanicos (
        tipo_operacion, usuario_operacion_id,
        id, nombre, direccion, telefono, email, especialidad, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo, activo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.nombre, NEW.direccion, NEW.telefono, NEW.email, NEW.especialidad, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo, NEW.activo
    );
END$$

CREATE TRIGGER trg_mecanicos_delete
BEFORE DELETE ON mecanicos
FOR EACH ROW
BEGIN
    INSERT INTO historico_mecanicos (
        tipo_operacion, usuario_operacion_id,
        id, nombre, direccion, telefono, email, especialidad, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo, activo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.nombre, OLD.direccion, OLD.telefono, OLD.email, OLD.especialidad, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo, OLD.activo
    );
END$$

-- TRIGGERS PARA TIPOS_TRABAJOS
CREATE TRIGGER trg_tipos_trabajos_insert
AFTER INSERT ON tipos_trabajos
FOR EACH ROW
BEGIN
    INSERT INTO historico_tipos_trabajos (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.nombre, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_tipos_trabajos_update
AFTER UPDATE ON tipos_trabajos
FOR EACH ROW
BEGIN
    INSERT INTO historico_tipos_trabajos (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.nombre, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_tipos_trabajos_delete
BEFORE DELETE ON tipos_trabajos
FOR EACH ROW
BEGIN
    INSERT INTO historico_tipos_trabajos (
        tipo_operacion, usuario_operacion_id,
        id, nombre, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.nombre, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA TRABAJOS_VEHICULOS
CREATE TRIGGER trg_trabajos_vehiculos_insert
AFTER INSERT ON trabajos_vehiculos
FOR EACH ROW
BEGIN
    INSERT INTO historico_trabajos_vehiculos (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, mecanico_id, tipo_trabajo_id, fecha_inicio, fecha_fin, descripcion, costo, estado, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.vehiculo_id, NEW.mecanico_id, NEW.tipo_trabajo_id, NEW.fecha_inicio, NEW.fecha_fin, NEW.descripcion, NEW.costo, NEW.estado, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_trabajos_vehiculos_update
AFTER UPDATE ON trabajos_vehiculos
FOR EACH ROW
BEGIN
    INSERT INTO historico_trabajos_vehiculos (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, mecanico_id, tipo_trabajo_id, fecha_inicio, fecha_fin, descripcion, costo, estado, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.vehiculo_id, NEW.mecanico_id, NEW.tipo_trabajo_id, NEW.fecha_inicio, NEW.fecha_fin, NEW.descripcion, NEW.costo, NEW.estado, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_trabajos_vehiculos_delete
BEFORE DELETE ON trabajos_vehiculos
FOR EACH ROW
BEGIN
    INSERT INTO historico_trabajos_vehiculos (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, mecanico_id, tipo_trabajo_id, fecha_inicio, fecha_fin, descripcion, costo, estado, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.vehiculo_id, OLD.mecanico_id, OLD.tipo_trabajo_id, OLD.fecha_inicio, OLD.fecha_fin, OLD.descripcion, OLD.costo, OLD.estado, OLD.notas, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA PIEZAS
CREATE TRIGGER trg_piezas_insert
AFTER INSERT ON piezas
FOR EACH ROW
BEGIN
    INSERT INTO historico_piezas (
        tipo_operacion, usuario_operacion_id,
        id, nombre, marca, modelo, estado, costo, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.nombre, NEW.marca, NEW.modelo, NEW.estado, NEW.costo, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_piezas_update
AFTER UPDATE ON piezas
FOR EACH ROW
BEGIN
    INSERT INTO historico_piezas (
        tipo_operacion, usuario_operacion_id,
        id, nombre, marca, modelo, estado, costo, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.nombre, NEW.marca, NEW.modelo, NEW.estado, NEW.costo, NEW.descripcion, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_piezas_delete
BEFORE DELETE ON piezas
FOR EACH ROW
BEGIN
    INSERT INTO historico_piezas (
        tipo_operacion, usuario_operacion_id,
        id, nombre, marca, modelo, estado, costo, descripcion, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.nombre, OLD.marca, OLD.modelo, OLD.estado, OLD.costo, OLD.descripcion, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA PIEZAS_USADAS
CREATE TRIGGER trg_piezas_usadas_insert
AFTER INSERT ON piezas_usadas
FOR EACH ROW
BEGIN
    INSERT INTO historico_piezas_usadas (
        tipo_operacion, usuario_operacion_id,
        id, trabajo_id, pieza_id, cantidad, costo_unitario, notas, usuario_registro_id, fecha_hora_registro
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.trabajo_id, NEW.pieza_id, NEW.cantidad, NEW.costo_unitario, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro
    );
END$$

CREATE TRIGGER trg_piezas_usadas_update
AFTER UPDATE ON piezas_usadas
FOR EACH ROW
BEGIN
    INSERT INTO historico_piezas_usadas (
        tipo_operacion, usuario_operacion_id,
        id, trabajo_id, pieza_id, cantidad, costo_unitario, notas, usuario_registro_id, fecha_hora_registro
    ) VALUES (
        'UPDATE', NEW.usuario_registro_id,
        NEW.id, NEW.trabajo_id, NEW.pieza_id, NEW.cantidad, NEW.costo_unitario, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro
    );
END$$

CREATE TRIGGER trg_piezas_usadas_delete
BEFORE DELETE ON piezas_usadas
FOR EACH ROW
BEGIN
    INSERT INTO historico_piezas_usadas (
        tipo_operacion, usuario_operacion_id,
        id, trabajo_id, pieza_id, cantidad, costo_unitario, notas, usuario_registro_id, fecha_hora_registro
    ) VALUES (
        'DELETE', OLD.usuario_registro_id,
        OLD.id, OLD.trabajo_id, OLD.pieza_id, OLD.cantidad, OLD.costo_unitario, OLD.notas, OLD.usuario_registro_id, OLD.fecha_hora_registro
    );
END$$

-- TRIGGERS PARA ALQUILERES
CREATE TRIGGER trg_alquileres_insert
AFTER INSERT ON alquileres
FOR EACH ROW
BEGIN
    INSERT INTO historico_alquileres (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, inquilino_id, estado_id, fecha_alquiler_inicio, fecha_alquiler_fin, semana, dia_trabajo, ingreso, monto_descuento, concepto_descuento, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.vehiculo_id, NEW.inquilino_id, NEW.estado_id, NEW.fecha_alquiler_inicio, NEW.fecha_alquiler_fin, NEW.semana, NEW.dia_trabajo, NEW.ingreso, NEW.monto_descuento, NEW.concepto_descuento, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_alquileres_update
AFTER UPDATE ON alquileres
FOR EACH ROW
BEGIN
    INSERT INTO historico_alquileres (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, inquilino_id, estado_id, fecha_alquiler_inicio, fecha_alquiler_fin, semana, dia_trabajo, ingreso, monto_descuento, concepto_descuento, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.vehiculo_id, NEW.inquilino_id, NEW.estado_id, NEW.fecha_alquiler_inicio, NEW.fecha_alquiler_fin, NEW.semana, NEW.dia_trabajo, NEW.ingreso, NEW.monto_descuento, NEW.concepto_descuento, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_alquileres_delete
BEFORE DELETE ON alquileres
FOR EACH ROW
BEGIN
    INSERT INTO historico_alquileres (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, inquilino_id, estado_id, fecha_alquiler_inicio, fecha_alquiler_fin, semana, dia_trabajo, ingreso, monto_descuento, concepto_descuento, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.vehiculo_id, OLD.inquilino_id, OLD.estado_id, OLD.fecha_alquiler_inicio, OLD.fecha_alquiler_fin, OLD.semana, OLD.dia_trabajo, OLD.ingreso, OLD.monto_descuento, OLD.concepto_descuento, OLD.notas, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA DEUDAS
CREATE TRIGGER trg_deudas_insert
AFTER INSERT ON deudas
FOR EACH ROW
BEGIN
    INSERT INTO historico_deudas (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, inquilino_id, alquiler_id, monto_deuda, dias_retraso, penalizacion_diaria, estado, fecha_vencimiento, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.vehiculo_id, NEW.inquilino_id, NEW.alquiler_id, NEW.monto_deuda, NEW.dias_retraso, NEW.penalizacion_diaria, NEW.estado, NEW.fecha_vencimiento, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_deudas_update
AFTER UPDATE ON deudas
FOR EACH ROW
BEGIN
    INSERT INTO historico_deudas (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, inquilino_id, alquiler_id, monto_deuda, dias_retraso, penalizacion_diaria, estado, fecha_vencimiento, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.vehiculo_id, NEW.inquilino_id, NEW.alquiler_id, NEW.monto_deuda, NEW.dias_retraso, NEW.penalizacion_diaria, NEW.estado, NEW.fecha_vencimiento, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_deudas_delete
BEFORE DELETE ON deudas
FOR EACH ROW
BEGIN
    INSERT INTO historico_deudas (
        tipo_operacion, usuario_operacion_id,
        id, vehiculo_id, inquilino_id, alquiler_id, monto_deuda, dias_retraso, penalizacion_diaria, estado, fecha_vencimiento, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.vehiculo_id, OLD.inquilino_id, OLD.alquiler_id, OLD.monto_deuda, OLD.dias_retraso, OLD.penalizacion_diaria, OLD.estado, OLD.fecha_vencimiento, OLD.notas, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

-- TRIGGERS PARA PAGOS
CREATE TRIGGER trg_pagos_insert
AFTER INSERT ON pagos
FOR EACH ROW
BEGIN
    INSERT INTO historico_pagos (
        tipo_operacion, usuario_operacion_id,
        id, alquiler_id, metodo_pago_id, monto, fecha_pago, deducciones, neto, comprobante, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'INSERT', NEW.usuario_registro_id,
        NEW.id, NEW.alquiler_id, NEW.metodo_pago_id, NEW.monto, NEW.fecha_pago, NEW.deducciones, NEW.neto, NEW.comprobante, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_pagos_update
AFTER UPDATE ON pagos
FOR EACH ROW
BEGIN
    INSERT INTO historico_pagos (
        tipo_operacion, usuario_operacion_id,
        id, alquiler_id, metodo_pago_id, monto, fecha_pago, deducciones, neto, comprobante, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'UPDATE', NEW.usuario_actualizo_id,
        NEW.id, NEW.alquiler_id, NEW.metodo_pago_id, NEW.monto, NEW.fecha_pago, NEW.deducciones, NEW.neto, NEW.comprobante, NEW.notas, NEW.usuario_registro_id, NEW.fecha_hora_registro, NEW.usuario_actualizo_id, NEW.fecha_hora_actualizo
    );
END$$

CREATE TRIGGER trg_pagos_delete
BEFORE DELETE ON pagos
FOR EACH ROW
BEGIN
    INSERT INTO historico_pagos (
        tipo_operacion, usuario_operacion_id,
        id, alquiler_id, metodo_pago_id, monto, fecha_pago, deducciones, neto, comprobante, notas, usuario_registro_id, fecha_hora_registro, usuario_actualizo_id, fecha_hora_actualizo
    ) VALUES (
        'DELETE', OLD.usuario_actualizo_id,
        OLD.id, OLD.alquiler_id, OLD.metodo_pago_id, OLD.monto, OLD.fecha_pago, OLD.deducciones, OLD.neto, OLD.comprobante, OLD.notas, OLD.usuario_registro_id, OLD.fecha_hora_registro, OLD.usuario_actualizo_id, OLD.fecha_hora_actualizo
    );
END$$

DELIMITER ;

USE alquiler_vehiculos;

ALTER TABLE propietarios
    MODIFY COLUMN cedula VARCHAR(255),
    MODIFY COLUMN licencia VARCHAR(255);

ALTER TABLE inquilinos
    MODIFY COLUMN cedula VARCHAR(255),
    MODIFY COLUMN licencia VARCHAR(255);

ALTER TABLE bancos
    MODIFY COLUMN cuenta VARCHAR(255),
    MODIFY COLUMN cedula VARCHAR(255);

-- Historical tables
ALTER TABLE historico_propietarios
    MODIFY COLUMN cedula VARCHAR(255),
    MODIFY COLUMN licencia VARCHAR(255);

ALTER TABLE historico_inquilinos
    MODIFY COLUMN cedula VARCHAR(255),
    MODIFY COLUMN licencia VARCHAR(255);

ALTER TABLE historico_bancos
    MODIFY COLUMN cuenta VARCHAR(255),
    MODIFY COLUMN cedula VARCHAR(255);
-- ================================================================================
-- SECCIÓN 4: DATOS INICIALES (INSERTS)
-- ================================================================================



-- Usuario administrador inicial (password: 'admin123' - CAMBIAR INMEDIATAMENTE)
INSERT INTO usuarios (username, password, rol, nombre, apellido, email, telefono, activo) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeshTgp9hcXF3Xq5dJCOXxZmK', 'admin', 'Administrador', 'Sistema', 'admin@alquiler.com', '809-000-0000', TRUE),
('user1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeshTgp9hcXF3Xq5dJCOXxZmK', 'user', 'Usuario', 'Prueba', 'user@alquiler.com', '809-111-1111', TRUE);

-- Estados de Alquiler
INSERT INTO estados_alquiler (nombre, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Pendiente', 'Alquiler pendiente de confirmación', 1, 1),
('En curso', 'Alquiler activo en progreso', 1, 1),
('Validado', 'Alquiler validado y confirmado', 1, 1),
('Pausado', 'Alquiler temporalmente pausado', 1, 1),
('Finalizado', 'Alquiler completado exitosamente', 1, 1),
('Cancelado', 'Alquiler cancelado antes de iniciar', 1, 1),
('Vencido', 'Alquiler vencido con deuda pendiente', 1, 1);

-- Métodos de Pago
INSERT INTO metodos_pago (nombre, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Efectivo', 'Pago en efectivo', 1, 1),
('Transferencia', 'Transferencia bancaria', 1, 1),
('Tarjeta débito', 'Pago con tarjeta de débito', 1, 1),
('Tarjeta crédito', 'Pago con tarjeta de crédito', 1, 1),
('Depósito', 'Depósito bancario', 1, 1),
('Cheque', 'Pago con cheque', 1, 1);

-- Tipos de Cuentas
INSERT INTO tipo_cuentas (tipo_cuenta, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Ahorros', 'Cuenta de ahorros', 1, 1),
('Corriente', 'Cuenta corriente', 1, 1),
('Nómina', 'Cuenta de nómina', 1, 1);

-- Bancos (ejemplos para República Dominicana)
INSERT INTO bancos (banco, cuenta, tipo_cuenta_id, cedula, administrador, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Banco Popular', '100-123456-7', 1, '001-1234567-8', 'Juan Pérez', 'Cuenta principal empresa', 1, 1),
('Banco BHD León', '200-654321-9', 2, '001-1234567-8', 'Juan Pérez', 'Cuenta secundaria', 1, 1),
('Banco Reservas', '300-789012-3', 1, '001-1234567-8', 'Juan Pérez', 'Cuenta de reservas', 1, 1),
('Banesco', '400-345678-1', 2, '001-1234567-8', 'Juan Pérez', 'Cuenta operativa', 1, 1);

-- Parentescos
INSERT INTO parentescos (parentesco, usuario_registro_id, usuario_actualizo_id) VALUES
('Padre', 1, 1), ('Madre', 1, 1), ('Hermano', 1, 1), ('Hermana', 1, 1),
('Hijo', 1, 1), ('Hija', 1, 1), ('Esposo', 1, 1), ('Esposa', 1, 1),
('Primo', 1, 1), ('Prima', 1, 1), ('Tío', 1, 1), ('Tía', 1, 1),
('Sobrino', 1, 1), ('Sobrina', 1, 1), ('Abuelo', 1, 1), ('Abuela', 1, 1),
('Nieto', 1, 1), ('Nieta', 1, 1), ('Cuñado', 1, 1), ('Cuñada', 1, 1),
('Suegro', 1, 1), ('Suegra', 1, 1), ('Yerno', 1, 1), ('Nuera', 1, 1),
('Amigo', 1, 1), ('Conocido', 1, 1), ('Compañero de trabajo', 1, 1), ('Jefe', 1, 1), ('Otro', 1, 1);

-- Vehículo Marca y Modelo
INSERT INTO vehiculo_marca_modelo (marca, modelo, tipo, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Toyota', 'Corolla', 'Sedán', 'Sedán compacto', 1, 1),
('Toyota', 'Yaris', 'Sedán', 'Sedán subcompacto', 1, 1),
('Toyota', 'RAV4', 'SUV', 'SUV compacta', 1, 1),
('Toyota', 'Hilux', 'Camioneta', 'Camioneta pickup', 1, 1),
('Honda', 'Civic', 'Sedán', 'Sedán compacto', 1, 1),
('Honda', 'Accord', 'Sedán', 'Sedán mediano', 1, 1),
('Honda', 'CR-V', 'SUV', 'SUV compacta', 1, 1),
('Hyundai', 'Elantra', 'Sedán', 'Sedán compacto', 1, 1),
('Hyundai', 'Tucson', 'SUV', 'SUV compacta', 1, 1),
('Hyundai', 'Santa Fe', 'SUV', 'SUV mediana', 1, 1),
('Nissan', 'Versa', 'Sedán', 'Sedán subcompacto', 1, 1),
('Nissan', 'Sentra', 'Sedán', 'Sedán compacto', 1, 1),
('Nissan', 'Frontier', 'Camioneta', 'Camioneta pickup', 1, 1),
('Kia', 'Rio', 'Sedán', 'Sedán subcompacto', 1, 1),
('Kia', 'Sportage', 'SUV', 'SUV compacta', 1, 1),
('Mitsubishi', 'Lancer', 'Sedán', 'Sedán compacto', 1, 1),
('Mitsubishi', 'Outlander', 'SUV', 'SUV mediana', 1, 1),
('Mitsubishi', 'L200', 'Camioneta', 'Camioneta pickup', 1, 1),
('Suzuki', 'Swift', 'Hatchback', 'Compacto hatchback', 1, 1),
('Suzuki', 'Vitara', 'SUV', 'SUV compacta', 1, 1),
('Chevrolet', 'Spark', 'Hatchback', 'Mini hatchback', 1, 1),
('Chevrolet', 'Aveo', 'Sedán', 'Sedán subcompacto', 1, 1),
('Chevrolet', 'Cruze', 'Sedán', 'Sedán compacto', 1, 1),
('Ford', 'Fiesta', 'Hatchback', 'Compacto hatchback', 1, 1),
('Ford', 'Focus', 'Sedán', 'Sedán compacto', 1, 1),
('Ford', 'Ranger', 'Camioneta', 'Camioneta pickup', 1, 1),
('Mazda', 'Mazda3', 'Sedán', 'Sedán compacto', 1, 1),
('Mazda', 'CX-5', 'SUV', 'SUV compacta', 1, 1),
('Volkswagen', 'Jetta', 'Sedán', 'Sedán compacto', 1, 1),
('Volkswagen', 'Tiguan', 'SUV', 'SUV compacta', 1, 1),
('Honda', 'CB190R', 'Moto', 'Moto naked', 1, 1),
('Yamaha', 'FZ150', 'Moto', 'Moto sport', 1, 1),
('Suzuki', 'GN125', 'Moto', 'Moto estándar', 1, 1),
('Bajaj', 'Pulsar 180', 'Moto', 'Moto sport', 1, 1);

-- Tipos de Trabajos
INSERT INTO tipos_trabajos (nombre, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Mantenimiento preventivo', 'Revisión general programada', 1, 1),
('Cambio de aceite', 'Cambio de aceite y filtro', 1, 1),
('Reparación de motor', 'Reparación o ajuste de motor', 1, 1),
('Reparación de frenos', 'Cambio o ajuste de sistema de frenos', 1, 1),
('Cambio de neumáticos', 'Reemplazo de neumáticos', 1, 1),
('Reparación eléctrica', 'Reparación de sistema eléctrico', 1, 1),
('Reparación de suspensión', 'Ajuste o cambio de suspensión', 1, 1),
('Cambio de batería', 'Reemplazo de batería', 1, 1),
('Alineación y balanceo', 'Alineación de ruedas y balanceo', 1, 1),
('Reparación de transmisión', 'Reparación de caja de cambios', 1, 1),
('Cambio de clutch', 'Reemplazo de embrague', 1, 1),
('Inspección técnica', 'Revisión técnica completa', 1, 1),
('Reparación de carrocería', 'Trabajo de hojalatería y pintura', 1, 1),
('Cambio de escape', 'Reemplazo de sistema de escape', 1, 1),
('Reparación de aire acondicionado', 'Reparación de sistema AC', 1, 1);

-- Mecánicos
INSERT INTO mecanicos (nombre, direccion, telefono, email, especialidad, activo, usuario_registro_id, usuario_actualizo_id) VALUES
('Taller El Buen Mecánico', 'Av. 27 de Febrero, Santo Domingo', '809-555-0001', 'buenmecanico@gmail.com', 'Reparación general', TRUE, 1, 1),
('AutoServicio Pérez', 'Calle Principal #45, Santiago', '809-555-0002', 'autoperez@hotmail.com', 'Motor y transmisión', TRUE, 1, 1),
('Frenos y Suspensiones RD', 'Av. Independencia #123, Santo Domingo', '809-555-0003', 'frenosrd@gmail.com', 'Frenos y suspensión', TRUE, 1, 1),
('Electricidad Automotriz López', 'Zona Colonial, Santo Domingo', '809-555-0004', 'lopez.electrico@yahoo.com', 'Sistema eléctrico', TRUE, 1, 1);

-- Piezas comunes
INSERT INTO piezas (nombre, marca, modelo, estado, costo, descripcion, usuario_registro_id, usuario_actualizo_id) VALUES
('Batería', 'Bosch', 'S4 005', 'nueva', 2500.00, 'Batería 12V 60Ah', 1, 1),
('Batería', 'LTH', 'L-48-550', 'nueva', 2200.00, 'Batería 12V 48Ah', 1, 1),
('Filtro de aceite', 'Mann', 'W 712/75', 'nueva', 350.00, 'Filtro de aceite estándar', 1, 1),
('Pastillas de freno', 'Brembo', 'P 23 142', 'nueva', 1800.00, 'Pastillas delanteras', 1, 1),
('Disco de freno', 'TRW', 'DF6444', 'nueva', 2400.00, 'Disco ventilado delantero', 1, 1),
('Neumático', 'Michelin', '185/65R15', 'nueva', 3500.00, 'Neumático radial', 1, 1),
('Neumático', 'Firestone', '195/65R15', 'nueva', 3200.00, 'Neumático radial', 1, 1),
('Amortiguador', 'Monroe', 'G16376', 'nueva', 1600.00, 'Amortiguador delantero', 1, 1),
('Bomba de agua', 'Gates', 'WP0051', 'nueva', 1200.00, 'Bomba de agua', 1, 1),
('Clutch kit', 'LUK', '624 3806 33', 'nueva', 4500.00, 'Kit completo de clutch', 1, 1);

-- ================================================================================
-- FIN DEL SCRIPT
-- ================================================================================

-- Para ejecutar este script:
-- mysql -u root -p < alquiler_vehiculos_completo.sql

-- Para verificar triggers instalados:
-- USE alquiler_vehiculos;
-- SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE 
-- FROM information_schema.TRIGGERS 
-- WHERE TRIGGER_SCHEMA = 'alquiler_vehiculos'
-- ORDER BY EVENT_OBJECT_TABLE;
