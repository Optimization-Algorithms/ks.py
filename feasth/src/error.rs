use std::convert;
use std::fmt;
use std::io::Error;
use std::num::ParseIntError;

#[derive(Debug)]
pub enum ParseError {
    IOError(Error),
    ParseError(ParseIntError),
}

impl convert::From<Error> for ParseError {
    fn from(e: Error) -> Self {
        Self::IOError(e)
    }
}

impl convert::From<ParseIntError> for ParseError {
    fn from(e: ParseIntError) -> Self {
        Self::ParseError(e)
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::IOError(err) => write!(f, "IO Error: {}", err),
            Self::ParseError(err) => write!(f, "Int Parse Error: {}", err),
        }
    }
}
