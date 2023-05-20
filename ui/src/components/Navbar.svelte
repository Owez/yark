<nav>
    <div class="sidebar" />
</nav>

<style lang="scss">
    $sidebar: 50px;
    $gap: 10px;
    $gap-double: $gap * 2;

    nav {
        height: 100vh;
        width: calc($sidebar + $gap-double);
        flex-shrink: 0;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .sidebar {
        height: calc(100vh - $gap-double);
        width: $sidebar;
        background-color: black;
        border-radius: 5px;
    }
</style>
