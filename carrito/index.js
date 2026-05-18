const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

const carritos = {};

app.get('/carrito/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    res.json(carritos[sessionId] || []);
});

app.post('/carrito/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const { producto } = req.body;
    if (!carritos[sessionId]) carritos[sessionId] = [];
    const existe = carritos[sessionId].find(p => p.id === producto.id);
    if (existe) {
        existe.cantidad += 1;
    } else {
        carritos[sessionId].push({ ...producto, cantidad: 1 });
    }
    res.json(carritos[sessionId]);
});

app.patch('/carrito/:sessionId/:productoId', (req, res) => {
    const { sessionId, productoId } = req.params;
    const { cantidad } = req.body;
    const item = carritos[sessionId]?.find(p => p.id === productoId);
    if (item) {
        const maxStock = item.cnt || 99;
        item.cantidad = Math.min(cantidad, maxStock);
    }
    res.json(carritos[sessionId] || []);
});

app.delete('/carrito/:sessionId/:productoId', (req, res) => {
    const { sessionId, productoId } = req.params;
    if (carritos[sessionId]) {
        carritos[sessionId] = carritos[sessionId].filter(p => p.id !== productoId);
    }
    res.json(carritos[sessionId] || []);
});

app.delete('/carrito/:sessionId', (req, res) => {
    carritos[req.params.sessionId] = [];
    res.json([]);
});

app.listen(3000, () => console.log('Carrito corriendo en puerto 3000'));