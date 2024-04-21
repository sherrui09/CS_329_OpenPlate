const express = require('express');
const path = require('path');
const app = express();

app.get("/", (req, res) => {
    let indexPath = path.join(__dirname, 'index.html');
    res.sendFile(indexPath);
});

app.listen(3000, () => {
    console.log("App listening on port 3000");
});
