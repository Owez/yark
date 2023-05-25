<script lang="ts">
    import StartCard from "./StartCard.svelte";

    export let big = false;
</script>

<StartCard
    title="Create new"
    description="Create an archive from scratch to save your channel/playlist"
    {big}
/>
