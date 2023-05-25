<script lang="ts">
    import type { RecentArchive } from "$lib/state";
    import LoadItem from "./LoadItem.svelte";
    import StartCard from "./StartCard.svelte";

    export let recentArchives: RecentArchive[];
    export let ball = 1
    export let big = false;
</script>

<StartCard
    title="Load existing"
    description="Manage/view an existing archive that you've already created"
    {ball}
    {big}
>
    {#each recentArchives as recentArchive}
        <LoadItem {recentArchive} />
    {/each}
</StartCard>
