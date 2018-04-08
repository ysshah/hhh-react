const express = require('express')
const app = express()
const sqlite3 = require('sqlite3').verbose()

const db = new sqlite3.Database('./fresh.db', sqlite3.OPEN_READONLY, err => {
  if (err) {
    console.error(err.message);
  }
  console.log('Connected to the fresh database.');
})

const sql = 'SELECT * FROM posts WHERE ? < create_time AND create_time < ? ORDER BY score DESC'

app.get('/posts/:start/:end', (req, res) => {
  db.all(sql, [req.params.start, req.params.end], (err, rows) => {
    if (err) {
      res.send('Error: ' + err)
    } else {
      res.send(rows)
    }
  })
})

app.listen(5000, () => console.log('Example app listening on port 5000!'))
