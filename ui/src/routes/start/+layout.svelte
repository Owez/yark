<div class="pane">
    <a href="/start" class="header">
        <h1>Yark</h1>
        <p>1.3.2</p>
    </a>
    <div class="cards">
        <slot />
    </div>
</div>

<style lang="scss">
    .pane {
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .header {
        display: flex;
        align-items: end;
        margin-bottom: 2rem;
        text-decoration: none;
        color:inherit;

        h1 {
            font-size: 1.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
            margin-bottom: -1.5px;
        }
    }

    .cards {
        display: grid;
        grid-template-columns: auto auto;
        gap: 20px;
    }
</style>
