use std::fs::File;
use std::io::Read;
use std::path::Path;

pub fn load_file(file_name: &Path) -> std::io::Result<String> {
    let mut file = File::open(file_name)?;
    let mut buff = String::new();
    file.read_to_string(&mut buff)?;
    Ok(buff)
}
