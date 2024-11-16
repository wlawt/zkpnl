use risc0_zkvm::guest::env;

fn main() {
    //get vals read in
    let inputs: Vec<f32> = env::read();


    let entry: f32 = inputs[0];
    let current: f32 = inputs[1];
    let pnl_provided: f32 = inputs[2];
    let lev: f32 = inputs[3];

    // Scale values to integers

    let pnl_calculated = ((current - entry) / entry) * 100.0 * lev;

    let error_margin = 0.15 * pnl_provided.abs();

    // Check if pnl matches within error margin
    if (pnl_provided - pnl_calculated).abs() > error_margin {
        panic!(
            "PNL verification failed: provided = {:.6}, calculated = {:.6}",
            pnl_provided, pnl_calculated
        );
    }

    // Commit to journal
    let success = true;
    env::commit(&success);
}
