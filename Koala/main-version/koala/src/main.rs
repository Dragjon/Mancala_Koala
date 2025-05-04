///////////////////////////////////////////////////
// Mancala framework and Koala engine by Dragjon //
//                                        v0.0.1 //
///////////////////////////////////////////////////

use std::time::{Instant, Duration};
use std::io;

#[derive(Clone)]
struct Mancala {
    turn: i32,
    board: [i32; 12],
    houses: [i32; 2],
}

// Function to move seeds
fn make_move(mut game: Mancala, idx: i32) -> Mancala {  // Use 'mut game'
    let current_player: i32 = game.turn;  // 'let' instead of 'const'
    let my_house: i32 = if current_player == 0 { 6 } else { 0 };
    let num_marbles: i32 = game.board[idx as usize];  // Convert idx to usize for indexing
    game.board[idx as usize] = 0;  // Indexing requires usize

    let mut current_pos = (idx + 1) % 12;
    let mut last_pos = 99;
    let mut house_visits = 0;
    let mut visited_house_last_turn = false;

    for i in 0..num_marbles {
        // Place marble in my house or current pit
        if (current_pos == my_house) && (last_pos != my_house) {
            game.houses[current_player as usize] += 1;
            last_pos = my_house;
            house_visits += 1;
            visited_house_last_turn = true;
            continue;
        }
        else if i <= num_marbles - house_visits + 1 {
            game.board[current_pos as usize] += 1;
            last_pos = current_pos;
            current_pos = (current_pos + 1) % 12;
            visited_house_last_turn = false;
        }
    }

    if (last_pos == my_house) && visited_house_last_turn {
        return game; // Player gets another turn
    }

    // Check for capture
    if (last_pos != 99) && (game.board[last_pos as usize] == 1) && (last_pos / 6 == current_player) && ((game.board[(11-last_pos) as usize] > 0)) {
        let opposite_pos: i32 = 11 - last_pos;
        game.houses[current_player as usize] += game.board[opposite_pos as usize] + 1;
        game.board[last_pos as usize] = 0;
        game.board[opposite_pos as usize] = 0;
    }

    game.turn ^= 1;
    return game;
}

// Print board
fn print_board(game: &Mancala){
    println!("-----------------------------------------------------");
    let turn = if game.turn == 0 { "Player 1" } else { "Player 2" };
    println!("Turn: {}", turn);
    let extra_padding = if game.houses[1] > 9 { " " } else { "" };
    print!("             {}",extra_padding);
    for i in (6..=11).rev() {
        if i < 10 {
            print!("  0{}", i);
        }
        else {
            print!("  {}", i);
        }
    }
    println!();

    // Top row - Opponent's side
    print!("             {}+",extra_padding);
    for i in (6..=11).rev() {
        print!(" {} +", game.board[i]);
    }
    println!(" ({}) Player 1", game.houses[0]);

    // Bottom row - Your side
    print!("Player 2 ({}) +", game.houses[1]);
    for i in 0..6 {
        print!(" {} +", game.board[i]);
    }
    println!();

    print!("             {}",extra_padding);
    for i in 0..6 {
        print!("  0{}", i);
    }
    println!();
    println!("-----------------------------------------------------")
}

// Creates a new instance of the mancala struct
fn new_mancala() -> Mancala {
    Mancala {
        turn: 0,
        board: [4; 12], 
        houses: [0, 0],
    }
}

// Winner of the game, returns 0 if 1st player wins, returns 1 if 2nd player wins
// returns 2 if draw, returns 3 if inconclusive
fn winner(game: &Mancala) -> i32 {
    if (game.houses[0] > 24) && (game.houses[1] < 25){
        return 0;
    }
    else if (game.houses[0] < 25) && (game.houses[1] > 24){
        return 1;
    }
    else if (game.houses[0] == 24) && (game.houses[1] == 24){
        return 2;
    }
    return 3;
}

// Move generation which outputs a vector of all possible moves
fn move_gen(game: &Mancala) -> Vec<usize> {
    // Determine the starting index based on current player
    let start = if game.turn == 0 { 0 } else { 6 } as usize;
    
    // Generate valid moves (indices with non-zero marbles)
    (start..start + 6)        // Range covering 6 pits for current player
        .filter(|&i| game.board[i] != 0)  // Filter pits with marbles
        .collect()             // Collect into Vec<usize>
}

// Performance testing with metrics
/* Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz   1.90 GHz
┌───────┬────────────┬────────────┬─────────┐
│ Depth │   Nodes    │    Time    │   NPS   │
├───────┼────────────┼────────────┼─────────┤
│     1 │          6 │      0ms   │ infM/s  │
│     2 │         35 │      0ms   │ infM/s  │
│     3 │        185 │      0ms   │ infM/s  │
│     4 │        942 │      0ms   │ infM/s  │
│     5 │       4690 │      0ms   │ infM/s  │
│     6 │      23233 │      2ms   │ 10.6M/s │
│     7 │     114430 │      8ms   │ 13.0M/s │
│     8 │     563055 │     42ms   │ 13.3M/s │
│     9 │    2763490 │    206ms   │ 13.4M/s │
│    10 │   13519612 │    889ms   │ 15.2M/s │
│    11 │   65870939 │   4273ms   │ 15.4M/s │
└───────┴────────────┴────────────┴─────────┘
*/
pub fn perft(game: &Mancala, max_depth: i32) {
    let mut total_nodes = 0;
    let start_time = Instant::now();
    
    println!("Running perft from depth 1 to {}:", max_depth);
    println!("┌───────┬────────────┬────────────┬─────────┐");
    println!("│ Depth │   Nodes    │    Time    │   NPS   │");
    println!("├───────┼────────────┼────────────┼─────────┤");

    for depth in 1..=max_depth {
        let depth_start = Instant::now();
        let nodes = perft_helper(game.clone(), depth);
        let depth_duration = depth_start.elapsed();
        
        total_nodes += nodes;
        print_depth_stats(depth, nodes, depth_duration);
    }

    let total_duration = start_time.elapsed();
    println!("└───────┴────────────┴────────────┴─────────┘");
    print_final_stats(total_nodes, total_duration);
}

// Recursive perft implementation
fn perft_helper(game: Mancala, depth: i32) -> i64 {
    if depth == 0 {
        return 1;
    }
    
    let move_list = move_gen(&game);
    if depth == 1 {
        return move_list.len() as i64;
    }

    let mut nodes = 0;
    for curr_move in &move_list {
        let new_game = make_move(game.clone(), *curr_move as i32);
        nodes += perft_helper(new_game, depth - 1);
    }
    nodes
}

// Helper struct for formatting nodes/second
struct NodesPerSecond(f64);

impl std::fmt::Display for NodesPerSecond {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self.0 {
            n if n >= 1_000_000.0 => write!(f, "{:.1}M/s", n / 1_000_000.0),
            n if n >= 1_000.0 => write!(f, "{:.1}K/s", n / 1_000.0),
            n => write!(f, "{:.0}/s", n),
        }
    }
}

// Print formatted depth statistics
fn print_depth_stats(depth: i32, nodes: i64, duration: Duration) {
    let ms = duration.as_millis();
    let nps = if ms > 0 {
        nodes as f64 / (duration.as_secs_f64())
    } else {
        f64::INFINITY
    };
    
    println!("│ {:5} │ {:>10} │ {:>6}ms   │ {:>10} │",
        depth,
        format!("{:}", nodes),
        ms,
        NodesPerSecond(nps)
    );
}

// Print final summary statistics
fn print_final_stats(total_nodes: i64, duration: Duration) {
    let total_secs = duration.as_secs_f64();
    let avg_nps = total_nodes as f64 / (total_secs);
    
    println!("\nTotal nodes: {}", total_nodes);
    println!("Total time:  {:.3}s", total_secs);
    println!("Average NPS: {}", NodesPerSecond(avg_nps));
}

// Engine tuned evaluation 
fn evaluate(game: &Mancala) -> i32 {
    let mut net_diff_seeds = 0;
    for i in 0..6 {
        net_diff_seeds += game.board[i as usize] - game.board[(i+6) as usize];
    }
    
    if game.turn == 0 {
        return 30 + 100*(game.houses[0] - game.houses[1]) + net_diff_seeds;
    }

    return 30 + 100*(game.houses[1] - game.houses[0]) - net_diff_seeds;
}

// Negamax search function
// returns (score, root-best-move)
fn search(mut game: Mancala, mut depth: i32, mut ply: i32, mut alpha: i32, mut beta: i32, mut color: i32) -> (i32, i32) {
    let mut max = -100000;
    let state = winner(&game);
    let mut best_move = 99;

    if (state == 0) || (state == 1) {
        return (-30000, best_move);
    }
    
    if state == 2 {
        return (0, best_move);
    }

    if depth <= 0 {
        return (evaluate(&game), best_move);
    }

    let mut copygame = game.clone();
    let mut move_list = move_gen(&copygame);
    let prevturn = copygame.turn;

    if move_list.len() == 0 {
        copygame.turn ^= 1;
        ply += 1;
        move_list = move_gen(&copygame);
    }

    for curr_move_ptr in &move_list {
        let curr_move = *curr_move_ptr as i32;
        let mut copygame2 = copygame.clone();
        copygame2 = make_move(copygame2, curr_move);

        // If we have another free turn
        if copygame2.turn == prevturn {
            let (score, search_best) = search(copygame2, depth - 1, ply + 1, alpha, beta, color);
            if score > max {
                max = score;
                best_move = curr_move;
                if score > alpha {
                    alpha = score;
                }
            }
        }

        else {
            let (mut score, search_best) = search(copygame2, depth - 1, ply + 1, -beta, -alpha, -color);
            score = -score;
            if score > max {
                max = score;
                best_move = curr_move;
                if score > alpha {
                    alpha = score;
                    if alpha >= beta {
                        break;
                    }
                }
            }
        }
    }

    return (max, best_move);

}

fn get_best_move(game: Mancala, depth: i32) -> (i32, i32) {
    return search(game, depth, 0, -100000, 100000, 1);
}

fn main() {
    let mut game = new_mancala();
    
    while winner(&game) == 3 {
        // No valid moves, skip turn
        let moves = move_gen(&game);
        if moves.is_empty() {
            game.turn ^= 1;
            continue;
        }

        println!();
        print_board(&game);

        if game.turn == 0 {
            // Our turn
            let valid_moves = moves;
            loop {
                println!("Your move {:?}: ", valid_moves);
                let mut input = String::new();
                io::stdin().read_line(&mut input)
                    .expect("Failed to read input");
                
                match input.trim().parse::<usize>() {
                    Ok(mv) if valid_moves.contains(&mv) => {
                        game = make_move(game, mv as i32);
                        break;
                    },
                    Ok(_) => println!("Invalid move. Try again."),
                    Err(_) => println!("Please enter a valid number"),
                }
            }
        } else {
            // AI turn
            println!("AI is thinking...");
            let current_game = game.clone();
            let best = get_best_move(current_game, 12);
            println!("AI chose move: {} || Score: {}", best.1, best.0);
            game = make_move(game, best.1);
            println!("Static eval: {}", evaluate(&game));
        }
    }

    // Game over
    print_board(&game);
    match winner(&game) {
        0 => println!("You win!"),
        1 => println!("AI wins!"),
        2 => println!("It's a draw!"),
        _ => unreachable!(),
    }
        
}