const express = require("express");
const fs = require("fs");

const app = express();

app.get("/share", (req, res) => {

    const share = JSON.parse(
        fs.readFileSync("share.json")
    );

    res.json({
    admin_id: share.admin_id,
    x: share.x.toString(),
    y: share.y.toString()
});

});

app.get("/health", (req, res) => {

    res.send("Node1 online");

});

app.listen(3001, () => {

    console.log(
        "Node1 running on port 3001"
    );

});

app.get("/shutdown", (req, res) => {

    res.send("Node shutting down...")

    process.exit(0)
})