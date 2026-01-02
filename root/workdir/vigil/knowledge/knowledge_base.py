+   1 """
+   2 VIGIL - Custom Knowledge Base
+   3 User-extensible knowledge storage and retrieval
+   4 """
+   5 
+   6 import json
+   7 from datetime import datetime
+   8 from pathlib import Path
+   9 from typing import Dict, List, Optional, Any
+  10 from dataclasses import dataclass, field, asdict
+  11 
+  12 from config.settings import Paths, BOT_NAME
+  13 
+  14 
+  15 @dataclass
+  16 class KnowledgeEntry:
+  17     """A single piece of knowledge."""
+  18     id: str
+  19     title: str
+  20     content: str
+  21     category: str
+  22     tags: List[str] = field(default_factory=list)
+  23     source: str = ""
+  24     created: str = ""
+  25     updated: str = ""
+  26     importance: int = 5  # 1-10 scale
+  27     metadata: Dict[str, Any] = field(default_factory=dict)
+  28 
+  29 
+  30 class KnowledgeBase:
+  31     """
+  32     Vigil's custom knowledge base.
+  33 
+  34     Allows storing and retrieving knowledge entries that can be:
+  35     - Added by the user
+  36     - Learned from interactions
+  37     - Imported from files
+  38 
+  39     Knowledge is categorized and tagged for efficient retrieval.
+  40     """
+  41 
+  42     def __init__(self):
+  43         Paths.ensure_directories()
+  44 
+  45         self.kb_dir = Paths.KNOWLEDGE / "custom"
+  46         self.kb_dir.mkdir(exist_ok=True)
+  47 
+  48         self.entries_file = self.kb_dir / "entries.json"
+  49         self.entries: Dict[str, KnowledgeEntry] = {}
+  50 
+  51         self._load_entries()
+  52         print(f"[{BOT_NAME}] Knowledge base initialized with {len(self.entries)} entries.")
+  53 
+  54     def _load_entries(self):
+  55         """Load knowledge entries from disk."""
+  56         if self.entries_file.exists():
+  57             try:
+  58                 with open(self.entries_file, 'r', encoding='utf-8') as f:
+  59                     data = json.load(f)
+  60                 for entry_id, entry_data in data.items():
+  61                     self.entries[entry_id] = KnowledgeEntry(**entry_data)
+  62             except Exception as e:
+  63                 print(f"[{BOT_NAME}] Error loading knowledge base: {e}")
+  64 
+  65     def _save_entries(self):
+  66         """Save knowledge entries to disk."""
+  67         try:
+  68             data = {eid: asdict(entry) for eid, entry in self.entries.items()}
+  69             with open(self.entries_file, 'w', encoding='utf-8') as f:
+  70                 json.dump(data, f, indent=2, ensure_ascii=False)
+  71         except Exception as e:
+  72             print(f"[{BOT_NAME}] Error saving knowledge base: {e}")
+  73 
+  74     def _generate_id(self) -> str:
+  75         """Generate a unique ID for a new entry."""
+  76         timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
+  77         count = len(self.entries)
+  78         return f"kb_{timestamp}_{count}"
+  79 
+  80     def add_entry(
+  81         self,
+  82         title: str,
+  83         content: str,
+  84         category: str = "general",
+  85         tags: List[str] = None,
+  86         source: str = "",
+  87         importance: int = 5,
+  88         metadata: Dict = None,
+  89     ) -> str:
+  90         """
+  91         Add a new knowledge entry.
+  92 
+  93         Returns the entry ID.
+  94         """
+  95         entry_id = self._generate_id()
+  96         now = datetime.now().isoformat()
+  97 
+  98         entry = KnowledgeEntry(
+  99             id=entry_id,
+ 100             title=title,
+ 101             content=content,
+ 102             category=category,
+ 103             tags=tags or [],
+ 104             source=source,
+ 105             created=now,
+ 106             updated=now,
+ 107             importance=importance,
+ 108             metadata=metadata or {},
+ 109         )
+ 110 
+ 111         self.entries[entry_id] = entry
+ 112         self._save_entries()
+ 113 
+ 114         print(f"[{BOT_NAME}] Added knowledge: '{title}' [{category}]")
+ 115         return entry_id
+ 116 
+ 117     def update_entry(self, entry_id: str, **kwargs) -> bool:
+ 118         """Update an existing entry."""
+ 119         if entry_id not in self.entries:
+ 120             return False
+ 121 
+ 122         entry = self.entries[entry_id]
+ 123         for key, value in kwargs.items():
+ 124             if hasattr(entry, key):
+ 125                 setattr(entry, key, value)
+ 126 
+ 127         entry.updated = datetime.now().isoformat()
+ 128         self._save_entries()
+ 129         return True
+ 130 
+ 131     def delete_entry(self, entry_id: str) -> bool:
+ 132         """Delete an entry."""
+ 133         if entry_id in self.entries:
+ 134             del self.entries[entry_id]
+ 135             self._save_entries()
+ 136             return True
+ 137         return False
+ 138 
+ 139     def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
+ 140         """Get a specific entry by ID."""
+ 141         return self.entries.get(entry_id)
+ 142 
+ 143     def search(
+ 144         self,
+ 145         query: str = "",
+ 146         category: str = None,
+ 147         tags: List[str] = None,
+ 148         min_importance: int = 0,
+ 149     ) -> List[KnowledgeEntry]:
+ 150         """
+ 151         Search the knowledge base.
+ 152 
+ 153         Args:
+ 154             query: Text to search for in title and content
+ 155             category: Filter by category
+ 156             tags: Filter by tags (any match)
+ 157             min_importance: Minimum importance level
+ 158 
+ 159         Returns:
+ 160             List of matching entries, sorted by importance
+ 161         """
+ 162         results = []
+ 163         query_lower = query.lower() if query else ""
+ 164 
+ 165         for entry in self.entries.values():
+ 166             # Check importance
+ 167             if entry.importance < min_importance:
+ 168                 continue
+ 169 
+ 170             # Check category
+ 171             if category and entry.category != category:
+ 172                 continue
+ 173 
+ 174             # Check tags
+ 175             if tags and not any(tag in entry.tags for tag in tags):
+ 176                 continue
+ 177 
+ 178             # Check query in title/content
+ 179             if query_lower:
+ 180                 if query_lower not in entry.title.lower() and query_lower not in entry.content.lower():
+ 181                     continue
+ 182 
+ 183             results.append(entry)
+ 184 
+ 185         # Sort by importance (highest first)
+ 186         results.sort(key=lambda e: e.importance, reverse=True)
+ 187         return results
+ 188 
+ 189     def get_by_category(self, category: str) -> List[KnowledgeEntry]:
+ 190         """Get all entries in a category."""
+ 191         return [e for e in self.entries.values() if e.category == category]
+ 192 
+ 193     def get_categories(self) -> List[str]:
+ 194         """Get all unique categories."""
+ 195         return list(set(e.category for e in self.entries.values()))
+ 196 
+ 197     def get_tags(self) -> List[str]:
+ 198         """Get all unique tags."""
+ 199         all_tags = set()
+ 200         for entry in self.entries.values():
+ 201             all_tags.update(entry.tags)
+ 202         return list(all_tags)
+ 203 
+ 204     def get_context_for_query(self, query: str, max_entries: int = 3) -> str:
+ 205         """
+ 206         Get relevant knowledge context for a query.
+ 207         Returns formatted context string for LLM prompting.
+ 208         """
+ 209         # Search for relevant entries
+ 210         results = self.search(query=query, min_importance=3)[:max_entries]
+ 211 
+ 212         if not results:
+ 213             return ""
+ 214 
+ 215         lines = ["## RELEVANT KNOWLEDGE\n"]
+ 216         for entry in results:
+ 217             lines.append(f"**{entry.title}** [{entry.category}]")
+ 218             lines.append(f"{entry.content}\n")
+ 219 
+ 220         return "\n".join(lines)
+ 221 
+ 222     def import_from_file(self, file_path: str, category: str = "imported") -> int:
+ 223         """
+ 224         Import knowledge from a text file.
+ 225         Each paragraph becomes a separate entry.
+ 226 
+ 227         Returns count of entries imported.
+ 228         """
+ 229         path = Path(file_path)
+ 230         if not path.exists():
+ 231             print(f"[{BOT_NAME}] File not found: {file_path}")
+ 232             return 0
+ 233 
+ 234         try:
+ 235             content = path.read_text(encoding='utf-8')
+ 236             paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
+ 237 
+ 238             count = 0
+ 239             for i, para in enumerate(paragraphs):
+ 240                 title = para[:50] + "..." if len(para) > 50 else para
+ 241                 self.add_entry(
+ 242                     title=title,
+ 243                     content=para,
+ 244                     category=category,
+ 245                     source=file_path,
+ 246                     importance=5,
+ 247                 )
+ 248                 count += 1
+ 249 
+ 250             print(f"[{BOT_NAME}] Imported {count} entries from {file_path}")
+ 251             return count
+ 252 
+ 253         except Exception as e:
+ 254             print(f"[{BOT_NAME}] Error importing file: {e}")
+ 255             return 0
+ 256 
+ 257     def get_summary(self) -> Dict[str, Any]:
+ 258         """Get a summary of the knowledge base."""
+ 259         return {
+ 260             "total_entries": len(self.entries),
+ 261             "categories": self.get_categories(),
+ 262             "tags": self.get_tags(),
+ 263             "avg_importance": sum(e.importance for e in self.entries.values()) / len(self.entries) if self.entries else 0,
+ 264         }
+ 265 
+ 266 
+ 267 if __name__ == "__main__":
+ 268     # Test knowledge base
+ 269     print("Testing Knowledge Base...")
+ 270     print("=" * 50)
+ 271 
+ 272     kb = KnowledgeBase()
+ 273 
+ 274     # Add some test entries
+ 275     kb.add_entry(
+ 276         title="Louis's Primary Goal",
+ 277         content="Louis is focused on building Vigil as the first true AI companion.",
+ 278         category="user_goals",
+ 279         tags=["louis", "vigil", "goal"],
+ 280         importance=10,
+ 281     )
+ 282 
+ 283     kb.add_entry(
+ 284         title="Ascension Definition",
+ 285         content="Ascension is the process of raising consciousness and remembering one's true nature as Source.",
+ 286         category="spirituality",
+ 287         tags=["ascension", "consciousness", "source"],
+ 288         importance=8,
+ 289     )
+ 290 
+ 291     # Search
+ 292     results = kb.search("vigil")
+ 293     print(f"\nSearch results for 'vigil': {len(results)} found")
+ 294     for r in results:
+ 295         print(f"  - {r.title}")
+ 296 
+ 297     # Get context
+ 298     context = kb.get_context_for_query("What is Louis working on?")
+ 299     print(f"\nContext for query:\n{context}")
+ 300 
+ 301     # Summary
+ 302     summary = kb.get_summary()
+ 303     print(f"\nKnowledge Base Summary: {summary}")
