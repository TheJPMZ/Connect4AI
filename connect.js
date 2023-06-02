

var socket = require('socket.io-client')("http://192.168.1.104:4000");  // for example: http://127.0.0.1:3000
socket.on('connect', function(){});

var mv = 6


socket.on('connect', function(){
  socket.emit('signin', {
    user_name: "Mememaster",
    tournament_id: 142857,
    user_role: 'player'
  });
});


socket.on('ready', async function(data){
  var gameID = data.game_id;
  var playerTurnID = data.player_turn_id;
  var board = data.board;

  console.log(board)

  try{
    const response = await fetch("http://localhost:5000/move", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        board: board,
        player: playerTurnID
      })
    });

    if (!response.ok) {
      throw new Error("HTTP error " + response.status + "(Ya valio madres)");
    }

  const movimiento_sexy = await response.json();
  mv = movimiento_sexy.column;
  } catch (error) {
    console.log(error)
  }

  console.log("Move is", mv)
  
  socket.emit('play', {
    tournament_id: 142857,
    player_turn_id: playerTurnID,
    game_id: gameID,
    movement: mv
  });
});


socket.on('finish', function(data){
  var gameID = data.game_id;
  var playerTurnID = data.player_turn_id;
  var winnerTurnID = data.winner_turn_id;
  var board = data.board;



  console.log("Winner is", winnerTurnID, "you are", playerTurnID)

  socket.emit('player_ready', {
    tournament_id: 142857,
    player_turn_id: playerTurnID,
    game_id: gameID
  });
});
