use pyo3::prelude::*;

#[derive(Debug)]
pub enum Error {
    GetCode(PyErr),
}

pub type Result<T> = std::result::Result<T, Error>;
