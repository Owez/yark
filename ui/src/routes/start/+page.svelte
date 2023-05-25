<script lang="ts">
    import CreateCard from "../../components/start/CreateCard.svelte";
    import LoadCard from "../../components/start/LoadCard.svelte";
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;
</script>

<CreateCard />
<LoadCard recentArchives={data.recentArchives} />
