// ====================================================================
// BANDEJA ADAPTADORA PARA CAJAS DE MERCADO (RSA - OpenSCAD Paramétrico)
// ====================================================================
// Permite montar una tarjeta KiCad dentro de una caja comercial
// (Gainta, Hammond, estanca IP67, etc.) sin perforar la base exterior.

// --------------------------------------------------------------------
// 1. PARÁMETROS DE LA CAJA COMERCIAL (Medidas en mm)
// --------------------------------------------------------------------
caja_interna_x       = 200.0;  // Ancho útil interior de la caja de mercado
caja_interna_y       = 120.0;  // Largo útil interior de la caja de mercado
caja_postes_dist_x   = 180.0;  // Distancia entre centros de postes de la caja en X
caja_postes_dist_y   = 100.0;  // Distancia entre centros de postes de la caja en Y
caja_tornillo_dia    = 3.5;    // Diámetro de tornillo de la caja (ej. M3.5 / M4)

// --------------------------------------------------------------------
// 2. PARÁMETROS DEL PCB (Extraídos de KiCad)
// --------------------------------------------------------------------
pcb_x                = 207.4;  // Largo del PCB (Edge.Cuts)
pcb_y                = 157.0;   // Ancho del PCB (Edge.Cuts)
pcb_margen_taladro   = 4.0;    // Distancia del borde del PCB a los orificios
pcb_tornillo_dia     = 3.0;    // Diámetro tornillos PCB (M3 = 3.0mm, M2.5 = 2.5mm)
pcb_separacion_base  = 6.0;    // Altura de los postes separadores bajo el PCB

// --------------------------------------------------------------------
// 3. PARÁMETROS DE LA BANDEJA (Impresión 3D)
// --------------------------------------------------------------------
grosor_bandeja       = 2.8;    // Espesor de la placa base de la bandeja
holgura_caja         = 1.0;    // Holgura perimetral para que calce suave
diametro_poste_pcb   = 7.0;    // Diámetro exterior del poste que sostiene el PCB
alivio_peso          = true;   // Activar ventanas para ahorrar filamento/resina

$fn = 40; // Resolución de curvas

// ====================================================================
// MÓDULO PRINCIPAL DE LA BANDEJA
// ====================================================================
module bandeja_adaptadora() {
    ancho_real = caja_interna_x - holgura_caja * 2;
    largo_real = caja_interna_y - holgura_caja * 2;

    difference() {
        union() {
            // Placa base de la bandeja
            rounded_rect([ancho_real, largo_real, grosor_bandeja], r=4.0);

            // Postes para sujetar el PCB
            postes_pcb(ancho_real, largo_real);
        }

        // Orificios para atornillar la bandeja a la caja comercial
        orificios_caja();

        // Orificios roscados / pasantes en los postes del PCB
        taladros_postes_pcb(ancho_real, largo_real);

        // Ventanas de alivio de peso y ventilación
        if (alivio_peso) {
            ventanas_alivio(ancho_real, largo_real);
        }
    }
}

// --------------------------------------------------------------------
// MÓDULOS AUXILIARES
// --------------------------------------------------------------------
module rounded_rect(size, r=3.0) {
    x = size[0];
    y = size[1];
    z = size[2];
    translate([-x/2, -y/2, 0])
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=z);
        translate([x-r, r, 0]) cylinder(r=r, h=z);
        translate([r, y-r, 0]) cylinder(r=r, h=z);
        translate([x-r, y-r, 0]) cylinder(r=r, h=z);
    }
}

module orificios_caja() {
    dx = caja_postes_dist_x / 2;
    dy = caja_postes_dist_y / 2;
    for (pos = [[dx, dy], [-dx, dy], [dx, -dy], [-dx, -dy]]) {
        translate([pos[0], pos[1], -1])
            cylinder(d=caja_tornillo_dia, h=grosor_bandeja + 2);
    }
}

module postes_pcb(bx, by) {
    dx = (pcb_x / 2) - pcb_margen_taladro;
    dy = (pcb_y / 2) - pcb_margen_taladro;
    for (pos = [[dx, dy], [-dx, dy], [dx, -dy], [-dx, -dy]]) {
        translate([pos[0], pos[1], grosor_bandeja])
            cylinder(d=diametro_poste_pcb, h=pcb_separacion_base);
    }
}

module taladros_postes_pcb(bx, by) {
    dx = (pcb_x / 2) - pcb_margen_taladro;
    dy = (pcb_y / 2) - pcb_margen_taladro;
    for (pos = [[dx, dy], [-dx, dy], [dx, -dy], [-dx, -dy]]) {
        translate([pos[0], pos[1], -1])
            cylinder(d=pcb_tornillo_dia, h=grosor_bandeja + pcb_separacion_base + 2);
    }
}

module ventanas_alivio(bx, by) {
    // 4 ventanas simétricas para ahorrar material y permitir paso de cables
    w_x = (pcb_x / 2) - 25;
    w_y = (pcb_y / 2) - 25;
    for (sx = [-1, 1]) {
        for (sy = [-1, 1]) {
            translate([sx * (w_x/2 + 10), sy * (w_y/2 + 10), -1])
                rounded_rect([w_x, w_y, grosor_bandeja + 2], r=5);
        }
    }
}

// Renderizar modelo
bandeja_adaptadora();
