use crate::error::ParseError;
use crate::file_utils::load_file;
use std::path::Path;

pub struct TotalSize {
    pub integer: TotalCount,
    pub continuous: TotalCount,
}

impl TotalSize {
    fn new() -> Self {
        Self {
            integer: TotalCount::new(),
            continuous: TotalCount::new(),
        }
    }

    fn add_integer(mut self, amt: usize) -> Self {
        if amt > 0 {
            self.integer.add(amt);
        }

        self
    }
    fn add_continuous(mut self, amt: usize) -> Self {
        if amt > 0 {
            self.continuous.add(amt);
        }

        self
    }
}

pub struct TotalCount {
    pub total: usize,
    pub count: usize,
}

impl TotalCount {
    fn new() -> Self {
        Self { total: 0, count: 0 }
    }
    fn add(&mut self, amt: usize) {
        self.total += amt;
        self.count += 1;
    }
}

pub fn get_average_sizes(file: &Path) -> Result<TotalSize, ParseError> {
    let data = load_file(file)?;
    parse_status_data(&data)
}

pub fn get_model_sizes(file: &Path) -> Result<Vec<(usize, Option<usize>)>, ParseError> {
    let data = load_file(file)?;
    data.lines().filter_map(parse_csv_line).collect()
}

fn parse_status_data(data: &str) -> Result<TotalSize, ParseError> {
    let output = data
        .lines()
        .filter_map(extract_size_and_status)
        .map(|parse| match parse {
            Ok((c, s)) => match s {
                0 => Ok((0, c)),
                1 => Ok((c, 0)),
                _ => Ok((0, 0)),
            },
            Err(err) => Err(err),
        })
        .try_fold(TotalSize::new(), |avg_size, count| {
            let (i, c) = count?;
            Ok(avg_size.add_continuous(c).add_integer(i))
        });
    output
}

fn extract_size_and_status(line: &str) -> Option<Result<(usize, usize), ParseError>> {
    if let Some(result) = parse_csv_line(line) {
        match result {
            Ok(res) => if let Some(output) = convert_status(res) {
                Some(Ok(output))
            } else {
                None
            },
            Err(err) => Some(Err(err))
        }
    } else {
        None
    }
}

fn convert_status(data: (usize, Option<usize>)) -> Option<(usize, usize)> {
    let (size, status) = data;
    if let Some(status) = status {
        Some((size, status))
    } else {
        None
    }
}

fn parse_csv_line(line: &str) -> Option<Result<(usize, Option<usize>), ParseError>> {
    let tokens: Vec<&str> = line.split(',').collect();
    if tokens.len() == 3 {
        Some(convert_csv_line(&tokens))
    } else {
        None
    }
}

fn convert_csv_line(tokens: &[&str]) -> Result<(usize, Option<usize>), ParseError> {
    let count = tokens[1].parse()?;
    let status = if tokens[2].len() > 0 {
        Some(tokens[2].parse()?)
    } else {
        None
    };
    Ok((count, status))
}

#[cfg(test)]
mod test {

    use super::*;

    #[test]
    fn test_parse_status_data() {
        let data = r#"0,10,0
        1,15,0
        2,10,1
        3,45,1
        4,60,0
        5,70,1
        6,100,
        7,14,2
        8,78,
        9,30,1
        "#;
        let avg_size = parse_status_data(data).unwrap();
        assert_eq!(avg_size.continuous.total, 85);
        assert_eq!(avg_size.continuous.count, 3);
        assert_eq!(avg_size.integer.total, 155);
        assert_eq!(avg_size.integer.count, 4);
    }
}
