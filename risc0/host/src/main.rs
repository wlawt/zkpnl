use risc0_zkvm::Prover;
use risc0_zkvm::serde::{to_vec, from_slice};
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    // Path to the compiled guest program
    let guest_path = "guest/target/riscv32im-unknown-none-elf/release/guest";

    // Instantiate the prover
    let mut prover = Prover::new(guest_path)?;

    // dummy inputs (test to see if the proof is generated)
    let entry: f32 = 100.0;
    let current: f32 = 120.0;
    let pnl: f32 = 20.0;

    // Pass inputs to the guest program
    prover.add_input(&to_vec(&entry)?);
    prover.add_input(&to_vec(&current)?);
    prover.add_input(&to_vec(&pnl)?);

    // Run the zkVM to generate a proof
    let receipt = prover.run()?;

    // Extract the result from the guest program
    let result: f32 = from_slice(&receipt.journal)?;
    println!("Calculated PNL: {}", result);

    // Verify the proof
    receipt.verify(guest_path)?;
    println!("Proof verified successfully!");

    Ok(())
}
