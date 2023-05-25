<script lang="ts">
    import {
        recentArchiveToState,
        type RecentArchive,
        saveArchiveState,
    } from "$lib/state";

    export let recentArchive: RecentArchive;

    async function loadArchive() {
        const state = await recentArchiveToState(recentArchive);
        if (state != null) {
            saveArchiveState(state, document);
        } else {
            console.log("archive not found"); // TODO: not found, error here
        }
    }
</script>

<button on:click={async () => await loadArchive()}>{recentArchive.name}</button>

<style lang="scss">
    button {
        $padding-v: 0.5rem;
        $padding-h: 0.75rem;
        padding-top: $padding-v;
        padding-bottom: $padding-v;
        padding-left: $padding-h;
        padding-right: $padding-h;
        background-color: rgb(245, 245, 245);
        border: none;
        box-sizing: border-box;
        border-radius: 5px;
        width: 100%;
        text-align: left;
        transition: 0.125s;

        &:hover {
            background-color: rgb(235, 235, 235);
        }
    }
</style>
