mod error;
mod file_utils;
mod log_parser;
mod mps_parser;

use std::path::PathBuf;
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
#[structopt(about = "Compute Continuous and Integer Feasibility Threshold")]
struct Arguments {
    #[structopt(help = "MPS file, used to find the correct number of variables")]
    mps_file: PathBuf,
    #[structopt(help = "CSV log file from Feature Kernel `LOG_FILE`")]
    log_file: PathBuf,
}

fn average(counter: log_parser::TotalCount) -> f64 {
    (counter.total as f64) / (counter.count as f64)
}

fn get_ratio(counter: log_parser::TotalCount, size: usize) -> f64 {
    let avg = average(counter);
    avg / (size as f64)
}

fn run_file_parse(args: Arguments) -> Result<(usize, log_parser::TotalSize), error::ParseError> {
    let count = mps_parser::get_variable_count(&args.mps_file)?;
    let tot_size = log_parser::get_average_sizes(&args.log_file)?;
    Ok((count, tot_size))
}

fn run() -> Result<(), error::ParseError> {
    let args = Arguments::from_args();

    let (count, tot_size) = run_file_parse(args)?;
    println!("Size: {}", count);

    let continuous_threshold = get_ratio(tot_size.continuous, count);
    let integer_threshold = get_ratio(tot_size.integer, count);

    println!("CFT: {}", continuous_threshold);
    println!("IFT: {}", integer_threshold);
    Ok(())
}

fn main() {
    match run() {
        Ok(()) => {}
        Err(err) => println!("{}", err),
    }
}
