//! Route file containing all axum routes needed for the API

/// Other/common routes which don't fit into other categories
pub mod misc {
    use axum::response::Redirect;

    /// Index page redirecting to Yark's GitHub
    pub async fn index() -> Redirect {
        Redirect::permanent("https://github.com/Owez/yark/")
    }
}

/// Base-level archive management into the manager
pub mod archive {}

/// Video management as part of a parent archive
pub mod video {}

/// Note management as part of a parent note
pub mod note {}
