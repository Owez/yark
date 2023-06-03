<script lang="ts">
    import Navbar from "../../components/Navbar.svelte";
</script>

<div class="panel">
    <Navbar />
    <main><slot /></main>
</div>

<style lang="scss">
    .panel {
        display: flex;
    }

    main {
        width: 100%;
        height: 100vh;
        box-sizing: border-box;
        padding: 20px;
    }
</style>
