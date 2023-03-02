#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::env;
use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;

fn main() {
    // Generate a random secret to use
    let session_admin_secret: String = thread_rng()
        .sample_iter(&Alphanumeric)
        .take(30)
        .map(char::from)
        .collect();
    env::set_var("YARK_ADMIN_SECRET", session_admin_secret.clone());

    // Build and launch the app
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_environment_variable])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

/// Gets an environment variable of `name` for SvelteKit during runtime
#[tauri::command]
fn get_environment_variable(name: &str) -> String {
    std::env::var(name).unwrap_or_else(|_| "".to_string())
}
