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
        box-sizing: border-box;
        padding: 10px;
        padding-left: 0;
        width:100%;
        height:100vh;;
    }
</style>
