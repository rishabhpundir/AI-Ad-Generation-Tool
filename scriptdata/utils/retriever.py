from scriptdata.utils.embeddings import generate_embedding, index

def retrieve_similar_ads(query, top_n=5):
    """
    Retrieves top N most similar ad scripts based on user query.
    """
    query_embedding = generate_embedding(query)

    # Search for similar ads (explicitly specifying namespace)
    results = index.query(
        namespace="",  # If using namespaces, replace with actual namespace
        vector=query_embedding,
        top_k=top_n,
        include_metadata=True
    )

    retrieved_ads = []
    for match in results["matches"]:
        metadata = match.get("metadata", {})  # ✅ Ensure metadata exists

        retrieved_ads.append({
            "filename": match["id"],
            "platform": metadata.get("platform", ""),
            "ad_type": metadata.get("ad_type", ""),
            "industry": metadata.get("industry", ""),
            "score": match.get("score", 0.0)  # ✅ Default to 0.0 if score is missing
        })

    return retrieved_ads
