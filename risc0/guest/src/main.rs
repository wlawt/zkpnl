#![no_std]
#![no_main]

use risc0_zkvm_guest::env;

// Entry point for the zkVM guest
risc0_zkvm_guest::entry!(main);

pub fn main() {
    
    //get vals read in
    let entry: f32 = env::read();
    let current: f32 = env::read();
    let pnl_provided: f32 = env::read();

    //pnl formula
    let pnl_calculated = ((current - entry) / entry) * 100.0;

    // check if pnl matches
    if (pnl_provided - pnl_calculated).abs() > 0.0001 {
        panic!("PNL verification failed: provided = {}, calculated = {}", pnl_provided, pnl_calculated);
    }

    // Commit to journal
    env::commit(&pnl_calculated);
}
