pub mod errors;

use errors::{Error, Result};
use pyo3::prelude::*;

const CODE: &str = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/lastgen.py"));

fn get_code<'p>(py: Python<'p>) -> Result<&'p PyModule> {
    PyModule::from_code(py, CODE, "lastgen.py", "lastgen").map_err(|err| Error::GetCode(err))
}

// TODO: writing this for the future (its been a month since ive worked on this): need to connect this stuff to python and make a few functions like "refresh_metadata" and "refresh_download" to hook onto in the api so job queues can be a thing in the manager

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn basic() {
        Python::with_gil(|py| {
            let code = get_code(py).unwrap();
            let channel = code
                .getattr("Channel")
                .unwrap()
                .call_method("_new_empty", (), None)
                .unwrap();
            channel.call_method("commit", (), None).unwrap();
        });
    }
}
