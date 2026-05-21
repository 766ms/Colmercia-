/* ═══════════════════════════════════════════════════
   COLMERCIA — app.js
   ═══════════════════════════════════════════════════ */

/* ── SHARED STATE (buyer profile ↔ admin panel) ── */
const ColMercia_State = {
  buyer: {
    name: '{{ user.first_name }}',
    email: '{{ user.email }}',
    phone: '{{ user.telefono }}',
    avatar: null,
    plan: 'Free',
    updatedAt: new Date().toISOString()
  },
  // Persist to sessionStorage so admin panel picks it up in the same session
  save() {
    try {
      sessionStorage.setItem('colmercia_buyer', JSON.stringify(this.buyer));
    } catch (e) { }
  },
  load() {
    try {
      const saved = sessionStorage.getItem('colmercia_buyer');
      if (saved) this.buyer = { ...this.buyer, ...JSON.parse(saved) };
    } catch (e) { }
  }
};
ColMercia_State.load();

/* ── DATA ── */
const TICK_MSGS = ["🚚 Envíos gratis en toda Colombia", "✨ Más de 200 tiendas verificadas", "🎁 Nuevos productos cada semana", "🔐 Pago 100% seguro", "🇨🇴 Apoya las microempresas colombianas", "⭐ Productos únicos y auténticos"];

const NEW_PRODS = [
  { ico: '🌸', name: 'Perfume Dulce Miel 50ml', brand: 'Essence CO', price: '$95.000', old: '', stock: 'ok', cnt: 14, store: 'Essence CO', storeLoc: 'Bucaramanga · Perfumería', desc: 'Fragancia dulce y envolvente, elaborada con ingredientes naturales del Caribe colombiano. Presentación de 50ml ideal para uso diario.' },
  { ico: '👗', name: 'Vestido Maxi Floral', brand: 'Moda Propia', price: '$138.000', old: '', stock: 'ok', cnt: 8, store: 'Moda Propia', storeLoc: 'Cali · Moda', desc: 'Diseño exclusivo inspirado en los jardines del Pacífico. Tela liviana y fresca, perfecta para el clima tropical colombiano.' },
  { ico: '👟', name: 'Zapatos Plataforma Beige', brand: 'Paso Firme', price: '$162.000', old: '$195.000', stock: 'low', cnt: 3, store: 'Paso Firme', storeLoc: 'Bucaramanga · Calzado', desc: 'Calzado artesanal de cuero genuino con plataforma de 4cm. Cómodo para largas jornadas y elegante para cualquier ocasión.' },
  { ico: '👜', name: 'Mini Bag Cadena Dorada', brand: 'Studio BH', price: '$118.000', old: '', stock: 'ok', cnt: 20, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Bolso mini en cuero sintético de alta calidad con cadena dorada ajustable. Capacidad para esenciales con diseño sofisticado.' },
  { ico: '📓', name: 'Box Organizador Escritorio', brand: 'Papel y Arte', price: '$48.000', old: '', stock: 'ok', cnt: 35, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Set organizador de escritorio con 4 compartimentos, fabricado en cartón premium reciclado. Diseño minimalista y funcional.' },
  { ico: '💄', name: 'Sérum Vitamina C 30ml', brand: 'Glam Medellín', price: '$62.000', old: '', stock: 'ok', cnt: 22, store: 'Glam Medellín', storeLoc: 'Medellín · Skincare', desc: 'Sérum antioxidante con 15% de Vitamina C pura. Ilumina el tono de la piel y reduce manchas con uso diario de 30 días.' },
];

const SELLERS = [
  { ico: '🌸', name: 'Yours Truly Set Edición Limitada', brand: 'r.e.m. beauty', price: '$189.900', old: '$230.000', stock: 'low', cnt: 5, store: 'r.e.m. beauty', storeLoc: 'Bogotá · Maquillaje', desc: 'Set de edición limitada con base, rubor y labial en tonos cálidos. Presentación de lujo con empaque biodegradable.' },
  { ico: '👜', name: 'Cartera Mini Piel Genuina Camel', brand: 'Studio BH', price: '$245.000', old: '', stock: 'ok', cnt: 23, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Cartera mini fabricada en piel genuina curtida artesanalmente. Color camel atemporal, cierre YKK y correa ajustable.' },
  { ico: '👟', name: 'Sneakers Blancas Premium', brand: 'Paso Firme', price: '$185.000', old: '$210.000', stock: 'ok', cnt: 11, store: 'Paso Firme', storeLoc: 'Bucaramanga · Calzado', desc: 'Sneakers en cuero genuino blanco con suela de goma vulcanizada. Plantilla anatómica para máxima comodidad.' },
  { ico: '📻', name: 'Parlante Bluetooth Portátil', brand: 'TechPyme', price: '$92.000', old: '', stock: 'out', cnt: 0, store: 'TechPyme', storeLoc: 'Bogotá · Tecnología', desc: 'Parlante inalámbrico con 12h de batería, resistencia al agua IPX5 y sonido 360°. Incluye cable de carga USB-C.' },
  { ico: '📓', name: 'Kit Planner Mensual + Stickers', brand: 'Papel y Arte', price: '$38.500', old: '', stock: 'ok', cnt: 34, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Kit completo con planner A5 mensual, 120 stickers decorativos y 3 marcadores brush. Ideal para organización creativa.' },
  { ico: '💄', name: 'Paleta Sombras 12 Tonos Nude', brand: 'Glam Medellín', price: '$67.000', old: '', stock: 'low', cnt: 3, store: 'Glam Medellín', storeLoc: 'Medellín · Maquillaje', desc: 'Paleta de 12 sombras en tonos nude y marrón, fórmula larga duración 24h. Altamente pigmentada y libre de parabenos.' },
];

const STORES_DATA = [
  {
    img: '/static/images/logo1.jpg',
    name: 'Luxedrop Beauty',
    tag: 'Maquillaje · Bogotá',
    stars: 5, reviews: 128, prods: 47,
    featured: CATS.maquillaje.filter(p => p.store === 'Luxedrop Beauty')
  },
  {
    img: '/static/images/logo2.jpg',
    name: 'Studio BH',
    tag: 'Carteras · Medellín',
    stars: 5, reviews: 95, prods: 32,
    featured: CATS.carteras.filter(p => p.store === 'Studio BH')
  },
  {
    img: '/static/images/logo3.jpg',
    name: 'Moda Propia',
    tag: 'Ropa · Cali',
    stars: 4, reviews: 74, prods: 61,
    featured: CATS.ropa.filter(p => p.store === 'Moda Propia')
  },
  {
    img: '/static/images/logo4.jpg',
    name: 'Papel y Arte',
    tag: 'Papelería · Barranquilla',
    stars: 5, reviews: 210, prods: 88,
    featured: CATS.papeleria.filter(p => p.store === 'Papel y Arte')
  },
  {
    img: '/static/images/logo5.jpg',
    name: 'TechPyme',
    tag: 'Tecnología · Bogotá',
    stars: 4, reviews: 53, prods: 24,
    featured: CATS.tecnologia.filter(p => p.store === 'TechPyme')
  },
  {
    img: '/static/images/logo4.jpg',
    name: 'Paso Firme',
    tag: 'Calzado · Bucaramanga',
    stars: 5, reviews: 162, prods: 55,
    featured: CATS.calzado.filter(p => p.store === 'Paso Firme')
  },
];

const CATS = {
  ropa: [
    { ico: '👗', name: 'Suéter Oversize Tejido', brand: 'Moda Propia', price: '$89.000', stock: 'ok', cnt: 18, store: 'Moda Propia', storeLoc: 'Cali · Moda', desc: 'Suéter oversize en hilo tejido artesanalmente. Suave al tacto y abrigador, disponible en tallas S–XL.' },
    { ico: '👗', name: 'Camisa Lino Manga Larga', brand: 'Moda Propia', price: '$72.000', stock: 'ok', cnt: 24, store: 'Moda Propia', storeLoc: 'Cali · Moda', desc: 'Camisa 100% lino lavado, ligera y transpirable. Ideal para el clima cálido colombiano, cierre de perlas.' },
    { ico: '👖', name: 'Pantalón Baggy Denim Azul', brand: 'Denim CO', price: '$115.000', stock: 'low', cnt: 4, store: 'Denim CO', storeLoc: 'Bogotá · Denim', desc: 'Pantalón baggy en denim premium lavado índigo. Corte relajado con pinzas delanteras y bolsillos amplios.' },
    { ico: '👚', name: 'Blusa Floral Manga Corta', brand: 'Moda Propia', price: '$58.000', stock: 'ok', cnt: 30, store: 'Moda Propia', storeLoc: 'Cali · Moda', desc: 'Blusa en tela viscosa con estampado floral inspirado en la flora del Pacifico colombiano.' },
    { ico: '🧥', name: 'Chaqueta Bomber Negra', brand: 'Urban Style', price: '$145.000', stock: 'ok', cnt: 9, store: 'Urban Style', storeLoc: 'Bogotá · Streetwear', desc: 'Chaqueta bomber en nylon ripstop, forro interior suave. Logo bordado en el pecho, cierre YKK.' },
    { ico: '🩳', name: 'Short Cargo Verde', brand: 'Denim CO', price: '$68.000', stock: 'low', cnt: 3, store: 'Denim CO', storeLoc: 'Bogotá · Denim', desc: 'Short cargo en gabardina verde militar con 6 bolsillos. Corte holgado y cinturilla elástica trasera.' },
  ],
  maquillaje: [
    { ico: '💄', name: 'Base de Maquillaje SPF30', brand: 'Glam Medellín', price: '$55.000', stock: 'ok', cnt: 22, store: 'Glam Medellín', storeLoc: 'Medellín · Maquillaje', desc: 'Base de cobertura media-alta con SPF30. Fórmula hidratante de larga duración, 20 tonos disponibles.' },
    { ico: '💋', name: 'Labial Líquido Matte Rojo', brand: 'r.e.m. beauty', price: '$38.000', stock: 'ok', cnt: 40, store: 'r.e.m. beauty', storeLoc: 'Bogotá · Maquillaje', desc: 'Labial líquido de alta pigmentación en rojo intenso. Fórmula no transferible, dura hasta 12 horas sin retoques.' },
    { ico: '✨', name: 'Paleta Iluminador 3 Tonos', brand: 'Luxedrop Beauty', price: '$78.000', stock: 'low', cnt: 6, store: 'Luxedrop Beauty', storeLoc: 'Bogotá · Maquillaje', desc: 'Paleta con 3 tonos iluminadores: champagne, dorado rosado y bronce. Partículas ultra-finas para acabado glow.' },
    { ico: '👁', name: 'Máscara de Pestañas Volume', brand: 'Glam Medellín', price: '$42.000', stock: 'ok', cnt: 15, store: 'Glam Medellín', storeLoc: 'Medellín · Maquillaje', desc: 'Máscara de pestañas con fórmula volumizadora y curvadora. Cepillo especial que separa y alarga cada pestaña.' },
    { ico: '💄', name: 'Contorno en Polvo Bronze', brand: 'r.e.m. beauty', price: '$48.000', stock: 'ok', cnt: 19, store: 'r.e.m. beauty', storeLoc: 'Bogotá · Maquillaje', desc: 'Polvo de contorno bronze con acabado mate, fórmula buildable. Esculpe y define el rostro de forma natural.' },
    { ico: '💧', name: 'Primer Poros Invisible', brand: 'Luxedrop Beauty', price: '$52.000', stock: 'out', cnt: 0, store: 'Luxedrop Beauty', storeLoc: 'Bogotá · Maquillaje', desc: 'Primer de base silicona que minimiza poros y prolonga el maquillaje hasta 16h. Textura gel, sin parabenos.' },
  ],
  carteras: [
    { ico: '👜', name: 'Bolso Tote Canvas Natural', brand: 'Studio BH', price: '$120.000', stock: 'ok', cnt: 12, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Bolso tote en canvas 100% algodón natural sin blanquear. Asas de cuero genuino, capacidad 20L.' },
    { ico: '👛', name: 'Clutch Cuero Dorado', brand: 'Studio BH', price: '$95.000', stock: 'low', cnt: 5, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Clutch en cuero sintético metalizado dorado con cierre de sobre. Bolsillo interior con cierre YKK.' },
    { ico: '🎒', name: 'Mochila Urbana Negra', brand: 'BagCo', price: '$135.000', stock: 'ok', cnt: 8, store: 'BagCo', storeLoc: 'Cali · Carteras', desc: 'Mochila urban con compartimento para laptop 15", puerto USB externo y tela impermeable.' },
    { ico: '👜', name: 'Cartera Baguette Beige', brand: 'Studio BH', price: '$145.000', stock: 'ok', cnt: 16, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Cartera estilo baguette en piel beige. Cierre magnético, correa de cadena dorada desmontable.' },
    { ico: '💼', name: 'Riñonera Mini Rosa', brand: 'BagCo', price: '$75.000', stock: 'ok', cnt: 25, store: 'BagCo', storeLoc: 'Cali · Carteras', desc: 'Riñonera compacta en rosa nude con correa ajustable. Perfecta para el día a día, cabe celular y billetera.' },
    { ico: '🛍', name: 'Shopper XL Denim', brand: 'Studio BH', price: '$108.000', stock: 'out', cnt: 0, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Shopper extra grande en denim lavado azul. Asas de algodón trenzado, forro interior estampado.' },
  ],
  calzado: [
    { ico: '👢', name: 'Botas Chelsea Café', brand: 'Paso Firme', price: '$210.000', stock: 'ok', cnt: 10, store: 'Paso Firme', storeLoc: 'Bucaramanga · Calzado', desc: 'Botas Chelsea en cuero genuino café, elástico lateral para fácil calce. Suela de goma antideslizante.' },
    { ico: '🩴', name: 'Sandalias Planas Nude', brand: 'Paso Firme', price: '$88.000', stock: 'ok', cnt: 20, store: 'Paso Firme', storeLoc: 'Bucaramanga · Calzado', desc: 'Sandalias en tiras de cuero nude tejido artesanalmente. Plantilla acolchada y suela de cuero flexible.' },
    { ico: '👞', name: 'Zapatos Oxford Negros', brand: 'Cuero MX', price: '$175.000', stock: 'low', cnt: 3, store: 'Cuero MX', storeLoc: 'Manizales · Calzado', desc: 'Oxford clásico en cuero negro pulido. Puntera redonda, cordones planos y suela de cuero cosida a mano.' },
    { ico: '🥿', name: 'Mocasines Cuero Marrón', brand: 'Paso Firme', price: '$158.000', stock: 'ok', cnt: 7, store: 'Paso Firme', storeLoc: 'Bucaramanga · Calzado', desc: 'Mocasines de cuero marrón con detalle de borla. Forro interior en piel suave, ideal para oficina.' },
    { ico: '👠', name: 'Tacones Stiletto Rojo', brand: 'Cuero MX', price: '$145.000', stock: 'ok', cnt: 11, store: 'Cuero MX', storeLoc: 'Manizales · Calzado', desc: 'Stiletto en charol rojo con tacón de 10cm. Punta fina, cierre en tobillo. Para noches especiales.' },
    { ico: '🩴', name: 'Alpargatas Trenzadas', brand: 'Paso Firme', price: '$65.000', stock: 'ok', cnt: 35, store: 'Paso Firme', storeLoc: 'Bucaramanga · Calzado', desc: 'Alpargatas artesanales tejidas en fique natural por comunidades artesanas del Caribe colombiano.' },
  ],
  papeleria: [
    { ico: '📓', name: 'Cuaderno Bullet Journal A5', brand: 'Papel y Arte', price: '$28.000', stock: 'ok', cnt: 50, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Bullet journal A5 con 200 páginas punteadas 90g/m², cubierta dura y marcador de seda. Sin ácido.' },
    { ico: '🖍', name: 'Set Lápices de Colores 24u', brand: 'Papel y Arte', price: '$22.000', stock: 'ok', cnt: 60, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Set 24 lápices de colores solubles en agua, mina 3mm, graduados en colores vibrantes para ilustración.' },
    { ico: '🎀', name: 'Washi Tape Pack x10', brand: 'Craft Studio', price: '$18.000', stock: 'ok', cnt: 80, store: 'Craft Studio', storeLoc: 'Bogotá · Craft', desc: 'Pack 10 washi tapes de 15mm, diseños florales colombianos. Removible sin dejar residuo.' },
    { ico: '📅', name: 'Planner Semanal Premium', brand: 'Papel y Arte', price: '$35.000', stock: 'low', cnt: 8, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Planner semanal A5 sin fechas, 52 semanas. Sección de metas, hábitos y notas. Espiral metálico.' },
    { ico: '⭐', name: 'Stickers Decorativos 200u', brand: 'Craft Studio', price: '$12.000', stock: 'ok', cnt: 120, store: 'Craft Studio', storeLoc: 'Bogotá · Craft', desc: '200 stickers impresos en papel adhesivo matte premium. Diseños inspirados en la flora colombiana.' },
    { ico: '🖊', name: 'Marcadores Brush Set 12u', brand: 'Papel y Arte', price: '$42.000', stock: 'ok', cnt: 30, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Set 12 marcadores brush con punta de nylon, tinta a base de agua. Colores vibrantes y recargables.' },
  ],
  tecnologia: [
    { ico: '🔌', name: 'Hub USB-C 7 Puertos', brand: 'TechPyme', price: '$85.000', stock: 'ok', cnt: 14, store: 'TechPyme', storeLoc: 'Bogotá · Tecnología', desc: 'Hub USB-C con 7 puertos: 3×USB-A 3.0, 2×USB-C, lector SD y HDMI 4K. Carcasa aluminio. Plug & Play.' },
    { ico: '💻', name: 'Soporte Laptop Aluminio', brand: 'TechPyme', price: '$72.000', stock: 'ok', cnt: 18, store: 'TechPyme', storeLoc: 'Bogotá · Tecnología', desc: 'Soporte ergonómico de aluminio para laptop hasta 17". Altura ajustable en 6 posiciones, plegable.' },
    { ico: '🔋', name: 'Cable USB-C Trenzado 2m', brand: 'TechPyme', price: '$28.000', stock: 'ok', cnt: 45, store: 'TechPyme', storeLoc: 'Bogotá · Tecnología', desc: 'Cable USB-C trenzado en nylon de 2 metros. Carga rápida 65W y transferencia de datos a 480Mbps.' },
    { ico: '🖱', name: 'Mouse Inalámbrico Slim', brand: 'PixelTech', price: '$65.000', stock: 'low', cnt: 5, store: 'PixelTech', storeLoc: 'Medellín · Tecnología', desc: 'Mouse inalámbrico 2.4GHz con sensor óptico 1600DPI. Ultra-delgado 14mm, batería 12 meses.' },
    { ico: '🎧', name: 'Auriculares In-Ear BT', brand: 'PixelTech', price: '$98.000', stock: 'ok', cnt: 22, store: 'PixelTech', storeLoc: 'Medellín · Tecnología', desc: 'Auriculares Bluetooth 5.2 con cancelación pasiva de ruido. Batería 6h + 18h en estuche. IPX4.' },
    { ico: '⚡', name: 'Cargador Inalámbrico 15W', brand: 'TechPyme', price: '$55.000', stock: 'out', cnt: 0, store: 'TechPyme', storeLoc: 'Bogotá · Tecnología', desc: 'Cargador inalámbrico Qi 15W compatible con iPhone y Android. Indicador LED, protección sobrecalentamiento.' },
  ],
  regalos: [
    { ico: '🌸', name: 'Set Bienestar Mujer', brand: 'Essence CO', price: '$120.000', old: '', stock: 'ok', cnt: 15, store: 'Essence CO', storeLoc: 'Bucaramanga · Bienestar', desc: 'Set premium con vela aromática, sérum facial y crema de manos. Empaque regalo incluido.' },
    { ico: '📓', name: 'Kit Papelería Creativa', brand: 'Papel y Arte', price: '$55.000', old: '', stock: 'ok', cnt: 20, store: 'Papel y Arte', storeLoc: 'Barranquilla · Papelería', desc: 'Kit con cuaderno A5, set 12 marcadores, 3 washi tapes y stickers. Perfecto para amantes del diseño.' },
    { ico: '💄', name: 'Set Maquillaje Básico', brand: 'Glam Medellín', price: '$89.000', old: '', stock: 'ok', cnt: 12, store: 'Glam Medellín', storeLoc: 'Medellín · Maquillaje', desc: 'Set básico con base, labial y máscara de pestañas. Tonos universales aptos para toda piel.' },
    { ico: '👜', name: 'Mini Bolso de Fiesta', brand: 'Studio BH', price: '$95.000', old: '', stock: 'low', cnt: 4, store: 'Studio BH', storeLoc: 'Medellín · Carteras', desc: 'Mini bolso de noche en satén con bordado floral y cadena dorada. Perfecto para eventos especiales.' },
    { ico: '🕯', name: 'Velas Aromáticas x3', brand: 'Aroma CO', price: '$48.000', old: '', stock: 'ok', cnt: 30, store: 'Aroma CO', storeLoc: 'Bogotá · Hogar', desc: 'Set 3 velas de soya aromatizadas: Café Colombiano, Flores Silvestres y Cedro. 40h de duración cada una.' },
    { ico: '💍', name: 'Set Accesorios Dorados', brand: 'Golden Co', price: '$75.000', old: '', stock: 'ok', cnt: 18, store: 'Golden Co', storeLoc: 'Cali · Joyería', desc: 'Set de 3 piezas: collar, aretes y pulsera en baño de oro 18k. Diseño minimalista geométrico.' },
  ]
};

const GIFT_PRODS = [
  { ico: '🌸', name: 'Set Bienestar Mujer', price: '$120.000' },
  { ico: '📓', name: 'Kit Papelería Creativa', price: '$55.000' },
  { ico: '💄', name: 'Set Maquillaje Básico', price: '$89.000' },
  { ico: '👜', name: 'Mini Bolso de Fiesta', price: '$95.000' },
  { ico: '🕯', name: 'Velas Aromáticas x3', price: '$48.000' },
  { ico: '💍', name: 'Set Accesorios Dorados', price: '$75.000' },
];

/* ── HELPERS ── */
function stockBadge(s, c) {
  if (s === 'out') return '<span class="sbdg sout">Agotado</span>';
  if (s === 'low') return `<span class="sbdg slow">${c} disponibles</span>`;
  return `<span class="sbdg sok">${c} disponibles</span>`;
}
function starsStr(n) { return '⭐'.repeat(n); }

/* ── TICKER ── */
(function () {
  const items = [...TICK_MSGS, ...TICK_MSGS];
  document.getElementById('tickTrack').innerHTML = items.map(m => `<span class="tick-item">${m}<span class="tick-sep">✦</span></span>`).join('');
})();

/* ── SLIDER ── */
let cur = 0, tot = 3, slTimer;
const SDUR = 5000;
function goSlide(n) {
  cur = n;
  document.getElementById('slidesTrack').style.transform = `translateX(-${cur * 100}%)`;
  document.querySelectorAll('.sdot').forEach((d, i) => d.classList.toggle('active', i === cur));
  resetProg();
}
function slideMove(d) { goSlide((cur + d + tot) % tot); resetTimer(); }
function resetTimer() { clearInterval(slTimer); slTimer = setInterval(() => slideMove(1), SDUR); }
function resetProg() {
  const p = document.getElementById('sprog');
  p.style.transition = 'none'; p.style.width = '0';
  requestAnimationFrame(() => requestAnimationFrame(() => { p.style.transition = `width ${SDUR}ms linear`; p.style.width = '100%'; }));
}
resetTimer(); resetProg();

/* ═══════════════════════════════════════════════════
   QUICK VIEW — Producto
   ═══════════════════════════════════════════════════ */
let qvCurrentProduct = null;

function openProductQV(prod) {
  qvCurrentProduct = prod;
  document.getElementById('qvTag').textContent = `Vista Rápida · ${prod.brand}`;
  document.getElementById('qvImg').textContent = prod.ico;
  document.getElementById('qvBrand').textContent = prod.brand;
  document.getElementById('qvName').textContent = prod.name;
  document.getElementById('qvPrice').textContent = prod.price;

  const oldEl = document.getElementById('qvOld');
  oldEl.textContent = prod.old || '';
  oldEl.style.display = prod.old ? 'inline' : 'none';

  const badges = document.getElementById('qvBadges');
  let badgeHTML = '';
  if (prod.stock === 'low') badgeHTML += `<span class="sbdg slow">${prod.cnt} disponibles</span>`;
  if (prod.stock === 'ok') badgeHTML += `<span class="sbdg sok">${prod.cnt} disponibles</span>`;
  if (prod.stock === 'out') badgeHTML += `<span class="sbdg sout">Agotado</span>`;
  badges.innerHTML = badgeHTML;

  document.getElementById('qvDesc').textContent = prod.desc || 'Producto artesanal colombiano de alta calidad.';
  document.getElementById('qvQty').textContent = '1';

  const addBtn = document.getElementById('qvAddBtn');
  addBtn.disabled = prod.stock === 'out';
  addBtn.style.opacity = prod.stock === 'out' ? '.5' : '1';

  document.getElementById('qvStoreIco').textContent = prod.ico;
  document.getElementById('qvStoreName').textContent = prod.store || prod.brand;
  document.getElementById('qvStoreLoc').textContent = prod.storeLoc || 'Colombia';

  // Reset wishlist button
  document.getElementById('qvWishBtn').classList.remove('wished');
  document.getElementById('qvWishBtn').textContent = '♡';

  openModal('quickViewModal');
}
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
  if (id === 'accountModal') {
    document.getElementById('authView').style.display = 'block';
    document.getElementById('dashView').style.display = 'none';
    switchTab('login');
  }
  if (id === 'payModal') {
    cargarResumenPago();
  }
}

function qvChangeQty(d) {
  const n = document.getElementById('qvQty');
  const max = qvCurrentProduct ? qvCurrentProduct.cnt : 99;
  n.textContent = Math.max(1, Math.min(parseInt(n.textContent) + d, max || 1));
}

function qvAddToCart() {
  if (!qvCurrentProduct || qvCurrentProduct.stock === 'out') return;
  addToCart(qvCurrentProduct);
  const btn = document.getElementById('qvAddBtn');
  btn.textContent = '✓ ¡Agregado!';
  btn.style.background = '#2E7D32';
  setTimeout(() => {
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg> Agregar al carrito`;
    btn.style.background = '';
  }, 1800);
}
function qvToggleWish(btn) {
  const wished = btn.classList.toggle('wished');
  btn.textContent = wished ? '♥' : '♡';
}

/* ── OPEN STORE QUICK VIEW ── */
function openStoreQV(store) {
  document.getElementById('sqvLogo').textContent = store.ico;
  document.getElementById('sqvName').textContent = store.name;
  document.getElementById('sqvTagTxt').textContent = store.tag;
  document.getElementById('sqvStars').textContent = starsStr(store.stars) + ` (${store.reviews})`;
  document.getElementById('sqvReviews').textContent = store.reviews;
  document.getElementById('sqvProds').textContent = store.prods;

  const grid = document.getElementById('sqvProdGrid');
  grid.innerHTML = (store.featured || []).map(p => `
    <div class="sqv-prod-item" onclick="closeModal('storeQuickViewModal');openProductQV(${JSON.stringify({ ...p, brand: store.name, store: store.name, storeLoc: store.tag, stock: 'ok', cnt: 10, desc: '' }).replace(/"/g, '&quot;')})">
      <div class="sqv-prod-ico">${p.ico}</div>
      <div class="sqv-prod-name">${p.name}</div>
      <div class="sqv-prod-price">${p.price}</div>
    </div>`).join('');

  openModal('storeQuickViewModal');
}

/* ── RENDER NEW PRODUCTS ── */
(function () {
  const g = document.getElementById('newGrid');
  if (!g) return;
  g.innerHTML = NEW_PRODS.map(p => `
    <div class="ncard" onclick="openProductQV(${JSON.stringify(p).replace(/"/g, '&quot;')})">
      <div class="qv-chip">👁 Vista rápida</div>
      <div class="nbadge">Nuevo</div>
      <button class="nwish" onclick="event.stopPropagation();this.textContent=this.textContent==='♡'?'♥':'♡'">♡</button>
      <div class="nimg">${p.ico}</div>
      <div class="ninfo">
        <div class="nbrand">${p.brand}</div>
        <div class="nname">${p.name}</div>
        <div class="nprice">${p.price}</div>
        <button class="nadd" onclick="event.stopPropagation();addToCart()">+ Agregar al carrito</button>
      </div>
    </div>`).join('');
})();

/* ── RENDER BEST SELLERS ── */
(function () {
  const g = document.getElementById('sellersGrid');
  if (!g) return;
  g.innerHTML = SELLERS.map((p, i) => {
    const rank = i < 3 ? `<div class="rbadge r${i + 1}">${i + 1}</div>` : '';
    const qrow = p.stock !== 'out' ? `<div class="qrow"><button class="qbtn" onclick="event.stopPropagation();pQty(this,-1,${p.cnt})">−</button><span class="qnum">1</span><button class="qbtn" onclick="event.stopPropagation();pQty(this,1,${p.cnt})">+</button><span class="qlbl">/ ${p.cnt} disp.</span></div>` : '';
    const addBtn = p.stock !== 'out' ? `<button class="padd" onclick="event.stopPropagation();addToCart()">+ Agregar al carrito</button>` : `<button class="padd" disabled>Sin stock</button>`;
    return `<div class="pcard" onclick="openProductQV(${JSON.stringify(p).replace(/"/g, '&quot;')})">${rank}<div class="qv-chip">👁 Vista rápida</div><div class="pimg">${p.ico}</div><div class="pinfo"><div class="pbrand">${p.brand}</div><div class="pname">${p.name}</div><div class="pprices"><span class="pprice">${p.price}</span>${p.old ? `<span class="pold">${p.old}</span>` : ''}</div>${stockBadge(p.stock, p.cnt)}</div>${qrow}${addBtn}</div>`;
  }).join('');
})();

/* ── RENDER STORES ── */
(function () {
  const g = document.getElementById('storesGrid');
  if (!g) return;
  g.innerHTML = STORES_DATA.map(s => `
    <div class="stcard" onclick="openStoreQV(${JSON.stringify(s).replace(/"/g, '&quot;')})">
      <div class="qv-chip">👁 Ver tienda</div>
      <div class="stlogo">${s.ico}</div>
      <div class="stname">${s.name}</div>
      <div class="sttag">${s.tag}</div>
      <div class="strate"><span class="stars">${starsStr(s.stars)}</span><span class="rcount">(${s.reviews})</span></div>
      <div class="stcnt">${s.prods} productos</div>
      <button class="stbtn" onclick="event.stopPropagation();openStoreQV(${JSON.stringify(s).replace(/"/g, '&quot;')})">Visitar tienda</button>
    </div>`).join('');
})();

/* ── RENDER GIFTS ── */
(function () {
  const g = document.getElementById('giftsGrid');
  if (!g) return;
  g.innerHTML = GIFT_PRODS.map(p => `
    <div class="gcard">
      <div class="gimg">${p.ico}</div>
      <div class="ginfo">
        <div class="gname">${p.name}</div>
        <div class="gprice">${p.price}</div>
        <button class="gbtn" onclick="openModal('payModal')">🎁 Regalar</button>
      </div>
    </div>`).join('');
})();

/* ── CATEGORY FILTER ── */
function showCat(cat, el) {
  document.querySelectorAll('.clink').forEach(l => l.classList.remove('active'));
  if (el) el.classList.add('active');
  if (cat === 'todos') { hideCat(); return; }
  if (cat === 'regalos') { document.getElementById('gifts').scrollIntoView({ behavior: 'smooth' }); return; }
  const data = CATS[cat];
  if (!data) { hideCat(); return; }
  const names = { ropa: 'Ropa y Accesorios', maquillaje: 'Maquillaje', carteras: 'Carteras y Bolsos', calzado: 'Calzado', papeleria: 'Papelería', tecnologia: 'Tecnología' };
  document.getElementById('catTitle').textContent = names[cat] || cat;
  const g = document.getElementById('catGrid');
  g.className = 'pgrid';
  g.innerHTML = data.map(p => {
    const qrow = p.stock !== 'out' ? `<div class="qrow"><button class="qbtn" onclick="event.stopPropagation();pQty(this,-1,${p.cnt})">−</button><span class="qnum">1</span><button class="qbtn" onclick="event.stopPropagation();pQty(this,1,${p.cnt})">+</button><span class="qlbl">/ ${p.cnt} disp.</span></div>` : '';
    const addBtn = p.stock !== 'out' ? `<button class="padd" onclick="event.stopPropagation();addToCart()">+ Agregar al carrito</button>` : `<button class="padd" disabled>Sin stock</button>`;
    return `<div class="pcard" onclick="openProductQV(${JSON.stringify(p).replace(/"/g, '&quot;')})"><div class="qv-chip">👁 Vista rápida</div><div class="pimg">${p.ico}</div><div class="pinfo"><div class="pbrand">${p.brand}</div><div class="pname">${p.name}</div><div class="pprices"><span class="pprice">${p.price}</span></div>${stockBadge(p.stock, p.cnt)}</div>${qrow}${addBtn}</div>`;
  }).join('');
  const sec = document.getElementById('catprods');
  sec.style.display = 'block';
  sec.scrollIntoView({ behavior: 'smooth' });
}
function hideCat() { document.getElementById('catprods').style.display = 'none'; }

/* ── CART ── */
async function openCart() {
  document.getElementById('cartOv').classList.add('open');
  document.getElementById('cartDrawer').classList.add('open');
  document.body.style.overflow = 'hidden';
  await renderCart();
}

function closeCart() {
  document.getElementById('cartOv').classList.remove('open');
  document.getElementById('cartDrawer').classList.remove('open');
  document.body.style.overflow = '';
}

async function renderCart() {
  const res = await fetch(`https://colmercia-carrito-production.up.railway.app/carrito/${SESSION_ID}`);
  const items = await res.json();
  const container = document.getElementById('cartItems');
  const cnt = document.getElementById('drawerCnt');

  if (items.length === 0) {
    container.innerHTML = '<div class="cempty"><div class="cempty-ico">🛒</div><p>Tu carrito está vacío.<br/>¡Explora y encuentra algo que te encante!</p></div>';
    cnt.textContent = '0 productos';
    return;
  }

  cnt.textContent = `${items.length} producto${items.length !== 1 ? 's' : ''}`;
  container.innerHTML = items.map(p => `
    <div class="citem">
      <div class="cimg" style="background-image:url('${p.img}');background-size:cover;background-position:center;"></div>
      <div class="cinfo">
        <div class="cname">${p.name}</div>
        <div class="cbrand">${p.brand}</div>
        <div class="crow">
          <div class="qc">
            <button class="qcb" onclick="cambiarCantidad('${p.id}',-1)">−</button>
            <span class="qcn">${p.cantidad}</span>
            <button class="qcb" onclick="cambiarCantidad('${p.id}',1)">+</button>
          </div>
          <span class="cprice">${p.price}</span>
          <button class="cdel" onclick="eliminarItem('${p.id}')">🗑</button>
        </div>
      </div>
    </div>
  `).join('');
}

async function eliminarItem(id) {
  await fetch(`https://colmercia-carrito-production.up.railway.app/carrito/${SESSION_ID}/${id}`, { method: 'DELETE' });
  await renderCart();
  await actualizarBadge();
}

async function cambiarCantidad(id, delta) {
  const res = await fetch(`https://colmercia-carrito-production.up.railway.app/carrito/${SESSION_ID}`);
  const items = await res.json();
  const item = items.find(p => p.id === id);
  if (!item) return;
  if (item.cantidad + delta <= 0) {
    await eliminarItem(id);
  } else {
    item.cantidad += delta;
    await fetch(`https://colmercia-carrito-production.up.railway.app/carrito/${SESSION_ID}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ producto: item })
    });
    await renderCart();
    await actualizarBadge();
  }
}

function pQty(btn, d, max) {
  const r = btn.parentElement, n = r.querySelector('.qnum');
  n.textContent = Math.max(1, Math.min(parseInt(n.textContent) + d, max));
}

/* ── MODALS ── */
async function cargarResumenPago() {
  const res = await fetch(`https://colmercia-carrito-production.up.railway.app/carrito/${SESSION_ID}`);
  const items = await res.json();
  const fmt = n => '$' + n.toLocaleString('es-CO');

  document.getElementById('payItems').innerHTML = items.map(p => {
    const precio = parseInt(p.price.replace(/\D/g, ''));
    return `<div class="pay-row"><span>${p.name} × ${p.cantidad}</span><span>${fmt(precio * p.cantidad)}</span></div>`;
  }).join('');

  const total = items.reduce((sum, p) => {
    return sum + (parseInt(p.price.replace(/\D/g, '')) * p.cantidad);
  }, 0);

  document.getElementById('payTotal').textContent = fmt(total);
  document.getElementById('payConfirmBtn').textContent = `Confirmar pago — ${fmt(total)}`;
}

/* ── AUTH ── */
function switchTab(t) {
  document.querySelectorAll('.mtab').forEach((el, i) => el.classList.toggle('active', i === (t === 'login' ? 0 : 1)));
  document.getElementById('tabLogin').style.display = t === 'login' ? 'block' : 'none';
  document.getElementById('tabReg').style.display = t === 'register' ? 'block' : 'none';
}
function setRole(r, btn) {
  document.querySelectorAll('.rtbtn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('buyerForm').style.display = r === 'buyer' ? 'block' : 'none';
  document.getElementById('sellerForm').style.display = r === 'seller' ? 'block' : 'none';
  if (r === 'seller') selStep(1);
}
function selStep(n) {
  [1, 2, 3].forEach(i => {
    document.getElementById(`ss${i}`).style.display = i === n ? 'block' : 'none';
    const el = document.getElementById(`st${i}`);
    el.className = 'step';
    if (i < n) el.classList.add('done');
    if (i === n) el.classList.add('active');
  });
}
async function doLogin() {
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  const res = await fetch('/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  if (data.ok) {
    window.location.href = data.redirect;
  } else {
    alert(data.error);
  }
}

function getCookie(name) {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith(name + '='))?.split('=')[1];
}

// Load from shared state
const b = ColMercia_State.buyer;
const firstName = b.name.split(' ')[0];
document.getElementById('profName').textContent = `Hola, ${firstName} 👋`;
document.getElementById('profEmail').textContent = b.email;
document.getElementById('secEmail').textContent = b.email;
const phoneEl = document.getElementById('secPhone');
if (phoneEl) phoneEl.textContent = b.phone;

// Avatar in dashboard
const dashAva = document.getElementById('dashAvatar');
if (dashAva) {
  if (b.avatar) {
    dashAva.innerHTML = `<img src="${b.avatar}" alt="avatar" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" />`;
  } else {
    dashAva.textContent = '👤';
  }
}
startClock();

function doLogout() {
  window.location.href = '/auth/logout/';
}
function submitSeller() {
  if (!document.getElementById('tcheck').checked) { alert('Acepta los Términos.'); return; }
  document.getElementById('authView').style.display = 'none';
  document.getElementById('dashView').style.display = 'block';
  document.getElementById('profName').textContent = '¡Solicitud enviada! 🎉';
  document.getElementById('profEmail').textContent = 'Revisaremos en 24–48 horas';
  document.querySelector('.prof-plan').textContent = '⏳ Vendedor Pendiente';
}

/* ── EDIT FIELD (Profile) ── */
let efCurrentField = null;

function openEditField(field) {
  efCurrentField = field;
  const b = ColMercia_State.buyer;
  const config = {
    email: { title: 'Editar Correo Electrónico', label: 'Nuevo correo electrónico', value: b.email, type: 'email' },
    phone: { title: 'Editar Teléfono', label: 'Nuevo número de teléfono', value: b.phone, type: 'tel' },
    name: { title: 'Editar Nombre', label: 'Nombre completo', value: b.name, type: 'text' },
  };
  const c = config[field] || { title: 'Editar', label: 'Valor', value: '', type: 'text' };
  document.getElementById('efTitle').textContent = c.title;
  document.getElementById('efLabel').textContent = c.label;
  const inp = document.getElementById('efInput');
  inp.type = c.type;
  inp.value = c.value;
  inp.placeholder = c.value;
  closeModal('accountModal');
  openModal('editFieldModal');
}

function saveEditField() {
  if (!efCurrentField) return;
  const val = document.getElementById('efInput').value.trim();
  if (!val) { alert('El campo no puede estar vacío.'); return; }

  const b = ColMercia_State.buyer;
  if (efCurrentField === 'email') {
    b.email = val;
    const el = document.getElementById('secEmail');
    if (el) el.textContent = val;
    const pe = document.getElementById('profEmail');
    if (pe) pe.textContent = val;
  } else if (efCurrentField === 'phone') {
    b.phone = val;
    const el = document.getElementById('secPhone');
    if (el) el.textContent = val;
  } else if (efCurrentField === 'name') {
    b.name = val;
    const el = document.getElementById('profName');
    if (el) el.textContent = `Hola, ${val.split(' ')[0]} 👋`;
  }
  b.updatedAt = new Date().toISOString();
  ColMercia_State.save();

  closeModal('editFieldModal');
  showToast(`✅ ${efCurrentField === 'email' ? 'Correo' : efCurrentField === 'phone' ? 'Teléfono' : 'Nombre'} actualizado correctamente`);
}

/* ── ADMIN USERS LIST (reflects buyer state) ── */
function renderAdminUsersList() {
  const container = document.getElementById('adminUsersList');
  if (!container) return;
  const b = ColMercia_State.buyer;
  const initial = b.name ? b.name.charAt(0).toUpperCase() : 'V';
  const avaContent = b.avatar
    ? `<img src="${b.avatar}" alt="avatar" />`
    : initial;

  container.innerHTML = `
    <div class="admin-user-row">
      <div class="admin-user-ava">${avaContent}</div>
      <div style="flex:1;">
        <div class="admin-user-name">${b.name}</div>
        <div class="admin-user-email">${b.email}</div>
        <div class="admin-user-phone">${b.phone}</div>
      </div>
      <div>
        <div class="admin-user-badge">Plan: ${b.plan}</div>
        <div style="font-size:.62rem;color:var(--mut);margin-top:3px;text-align:right;">
          Actualizado: ${new Date(b.updatedAt).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })}
        </div>
      </div>
    </div>
    <div class="admin-user-row" style="opacity:.55;">
      <div class="admin-user-ava">C</div>
      <div style="flex:1;">
        <div class="admin-user-name">Carlos Mendoza</div>
        <div class="admin-user-email">carlos@empresa.com</div>
        <div class="admin-user-phone">+57 310 987 6543</div>
      </div>
      <div class="admin-user-badge">Plan: Pro</div>
    </div>
    <div class="admin-user-row" style="opacity:.55;">
      <div class="admin-user-ava">S</div>
      <div style="flex:1;">
        <div class="admin-user-name">Sandra Gómez</div>
        <div class="admin-user-email">sandra@correo.com</div>
        <div class="admin-user-phone">+57 320 456 7890</div>
      </div>
      <div class="admin-user-badge">Plan: Standard</div>
    </div>`;
}

/* ── TOAST NOTIFICATION ── */
function showToast(msg) {
  let t = document.getElementById('cm-toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'cm-toast';
    t.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:#1A1A2E;color:#fff;padding:12px 22px;border-radius:50px;font-size:.82rem;font-weight:600;z-index:9999;transition:transform .3s cubic-bezier(.34,1.2,.64,1),opacity .3s;opacity:0;pointer-events:none;white-space:nowrap;box-shadow:0 8px 32px rgba(0,0,0,.22);';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  requestAnimationFrame(() => {
    t.style.opacity = '1';
    t.style.transform = 'translateX(-50%) translateY(0)';
  });
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateX(-50%) translateY(80px)';
  }, 2800);
}

/* ── CLOCK ── */
let clockTimer;
function startClock() {
  function tick() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    const el = document.getElementById('profTime');
    if (el) el.textContent = `${h}:${m}:${s}`;
    const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    const de = document.getElementById('profDate');
    if (de) de.textContent = `${days[now.getDay()]} ${now.getDate()} ${months[now.getMonth()]}`;
  }
  tick();
  clockTimer = setInterval(tick, 1000);
}

/* ── PAYMENT ── */
function selectPay(el, type) {
  document.querySelectorAll('.pay-opt').forEach(o => o.classList.remove('sel'));
  el.classList.add('sel');
  ['payCard', 'payNequi', 'payDaviplata', 'payPse'].forEach(id => {
    const f = document.getElementById(id);
    if (f) f.classList.remove('show');
  });
  const map = { card: 'payCard', nequi: 'payNequi', daviplata: 'payDaviplata', pse: 'payPse' };
  const t = document.getElementById(map[type]);
  if (t) t.classList.add('show');
}
function toggleGiftMsg() {
  const box = document.getElementById('giftMsgBox');
  if (box) box.classList.toggle('show', document.getElementById('giftCheck').checked);
}

/* ── CHATBOT ── */
let cbCur = 1;
function openChatbot() {
  document.getElementById('chatbot-win').classList.add('open');
  cbCur = 1;
  showCbStep(1);
}
function closeChatbot() { document.getElementById('chatbot-win').classList.remove('open'); }
function showCbStep(n) {
  document.querySelectorAll('.cb-step').forEach((s, i) => s.classList.toggle('active', i === n - 1));
  document.getElementById('cbRecs').classList.remove('show');
}
function cbSelect(btn, step) {
  btn.closest('.cb-opts').querySelectorAll('.cb-opt').forEach(b => b.classList.remove('sel'));
  btn.classList.add('sel');
  setTimeout(() => {
    if (step < 3) { cbCur = step + 1; showCbStep(cbCur); }
    else { document.querySelectorAll('.cb-step').forEach(s => s.classList.remove('active')); document.getElementById('cbRecs').classList.add('show'); }
  }, 400);
}