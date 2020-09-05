mod error;
mod file_utils;
mod log_parser;
mod mps_parser;

use std::io::{Write, stdout};
use std::fs::File;
use std::path::PathBuf;
use structopt::{StructOpt, clap::ArgGroup};

#[derive(Debug, StructOpt)]
#[structopt(group = ArgGroup::with_name("file").required(true))]
struct ModelSize {
    #[structopt(help="Specify model size directly", name="Model size", short="s", long="size", group = "file")]
    size: Option<usize>,
    #[structopt(help="Specify MPS file and compute model size automatically", short="i", name="Model File", long="instance", group = "file")]
    file: Option<PathBuf>

}

#[derive(Debug, StructOpt)]
struct Arguments {
    #[structopt(flatten)]
    mps_file: ModelSize,
    #[structopt(help = "CSV log file from Feature Kernel `LOG_FILE`")]
    log_file: PathBuf,
    #[structopt(help = "Specify output file", short="-o", long="--output")]
    output: Option<PathBuf>
}


#[derive(Debug, StructOpt)]
#[structopt(about = "Compute USage Ratios, IFT and CFT")]
enum Action {
    #[structopt(about="compute IFT and CFT", name="thresh")]
    FeasThreshold(Arguments),
    #[structopt(about="compute Usage Ratios", name="ratio")]
    UsageRatio(Arguments)
}

fn get_output(args: &Arguments) -> std::io::Result<Box<dyn Write>> {
    let output: Box<dyn Write> = if let Some(ref name) = &args.output {
        Box::new(File::create(name)?)
    } else {    
        Box::new(stdout())
    };

    Ok(output)
}


fn average(counter: log_parser::TotalCount) -> Option<f64> {
    if counter.count == 0 {
        None
    } else {
        Some((counter.total as f64) / (counter.count as f64))
    }
}

fn get_ratio(counter: log_parser::TotalCount, size: usize) -> Option<f64> {
    let avg = average(counter)?;
    Some(avg / (size as f64))
}

fn print_index(name: &str, value: Option<f64>, output: &mut dyn Write) -> Result<(), error::ParseError> {
    write!(output, "{}: ", name)?;
    if let Some(value) = value {
        writeln!(output, "{}", value)?;   
    } else {
        writeln!(output, "UNDEFINED")?;
    }
    Ok(())
}

fn variable_count(mps_file: &ModelSize) -> Result<usize, error::ParseError> {
    if let Some(count) = mps_file.size {
        Ok(count)
    } else if let Some(ref file) = mps_file.file {
        mps_parser::get_variable_count(file)
    } else {
        unreachable!()
    }
}

fn compute_usage_ratio(args: Arguments) -> Result<Vec<(f64, Option<usize>)>, error::ParseError> {
    let count = variable_count(&args.mps_file)? as f64;
    let vect = log_parser::get_model_sizes(&args.log_file)?;
    let output = vect.iter().map(|(curr, status)| ((*curr as f64) / count, *status)).collect();
    Ok(output)
}


fn run_file_parse(args: Arguments) -> Result<(usize, log_parser::TotalSize), error::ParseError> {
    let count = variable_count(&args.mps_file)?;
    let tot_size = log_parser::get_average_sizes(&args.log_file)?;
    Ok((count, tot_size))
}

fn largest_index(cft: &Option<f64>, ift: &Option<f64>) -> Option<f64> {
    match (cft, ift) {
        (Some(cft), Some(ift)) => Some(if cft > ift {*cft} else {*ift}),
        (Some(cft), None) => Some(*cft),
        (None, Some(ift)) => Some(*ift),
        (None, None) => None
    }
}

fn warn_size(cft: &Option<f64>, ift: &Option<f64>) {
    let avg = largest_index(cft, ift);
    if let Some(avg) = avg {
        if avg > 1.0 {
            println!("Model is smaller than the average sub model size");
            println!("Possible Causes:");
            println!("\tMPS is not standard");
            println!("\tMPS and CSV are not for the same problem");
            println!("Consider to provide the model size directly");
        }
    }
}

fn run_threshold(args: Arguments) -> Result<(), error::ParseError> {
    let mut output = get_output(&args)?;
    let (count, tot_size) = run_file_parse(args)?;
    writeln!(&mut output, "Model Size: {}", count)?;

    let continuous_threshold = get_ratio(tot_size.continuous, count);
    let integer_threshold = get_ratio(tot_size.integer, count);

    warn_size(&continuous_threshold, &integer_threshold);

    print_index("CFT", continuous_threshold, &mut output)?;
    print_index("IFT", integer_threshold, &mut output)?;
    
    Ok(())
}


fn run_usage(args: Arguments) -> Result<(), error::ParseError> {

    let mut output = get_output(&args)?;
    let usage_ratio = compute_usage_ratio(args)?;
    for (ratio, status) in usage_ratio {
        if let Some(stat) = status {
            writeln!(&mut output, "{},{}", ratio, stat)?;
        } else {
            writeln!(&mut output, "{},", ratio)?;
        }
        
    }
    Ok(())
}

fn run() -> Result<(), error::ParseError> {
    let args = Action::from_args();
    match args {
        Action::FeasThreshold(arg) => run_threshold(arg),
        Action::UsageRatio(arg) => run_usage(arg)
    }
}

fn main() {
    match run() {
        Ok(()) => {}
        Err(err) => println!("{}", err),
    }
}
