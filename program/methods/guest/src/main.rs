use risc0_zkvm::guest::env;

fn main() {
    //get vals read in
    let inputs: Vec<f32> = env::read();

    let entry: f32 = inputs[0];
    let current: f32 = inputs[1];
    let pnl_provided: f32 = inputs[2];

    //pnl formula
    let pnl_calculated = ((current - entry) / entry) * 100.0;

    // check if pnl matches
    if (pnl_provided - pnl_calculated).abs() > 0.0001 {
        panic!("PNL verification failed: provided = {}, calculated = {}", pnl_provided, pnl_calculated);
    }

    // Commit to journal
    env::commit(&pnl_calculated);
}
