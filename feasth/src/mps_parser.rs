use std::path::Path;

use crate::error::ParseError;
use crate::file_utils::load_file;

pub fn get_variable_count(mps_file: &Path) -> Result<usize, ParseError> {
    let file_data = load_file(mps_file)?;

    let mut filter = FilterSection::new();
    let mut prev: Option<&str> = None;
    let output: usize = file_data
        .lines()
        .filter(|l| filter.filter(l))
        .filter(|l| l.len() >= 22)
        .filter(|l| &l[14..22] != "'MARKER'")
        .map(|l| &l[4..12])
        .filter(|var| {
            if let Some(p_var) = prev {
                if &p_var == var {
                    false
                } else {
                    prev = Some(var);
                    true
                }
            } else {
                prev = Some(var);
                true
            }
        })
        .count();
    Ok(output)
}

struct FilterSection {
    status: bool,
    next: bool,
}

impl FilterSection {
    fn new() -> Self {
        Self {
            status: false,
            next: false,
        }
    }

    fn filter(&mut self, line: &str) -> bool {
        self.status = if self.status {
            match line {
                "NAME" | "ROWS" | "RHS" | "BOUNDS" | "RANGES" | "ENDATA" => false,
                _ => true,
            }
        } else {
            let output = self.next;
            self.next = "COLUMNS" == line;
            output
        };
        self.status
    }
}

#[cfg(test)]
mod test {

    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_count() {
        let test_root = PathBuf::from("instances");
        if !test_root.exists() {
            return;
        }
        let file_path = test_root.join("instances.txt");
        let data = load_file(&file_path).unwrap();
        for line in data.lines() {
            let (file_name, size) = parse_line(line, &test_root);

            let ans = get_variable_count(&file_name).unwrap();
            assert_eq!(ans, size);
        }
    }

    fn parse_line(line: &str, root: &Path) -> (PathBuf, usize) {
        let index = line.find(':').unwrap();
        let instance = &line[..index];
        let inst_path = root.join(instance);
        let size = &line[index + 1..];
        let size: usize = size.parse().unwrap();
        (inst_path, size)
    }
}
