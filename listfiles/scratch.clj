(ns user
  (:require [yaml.core :as yaml]
            [table.core :as t]
            [table.width :refer [*width*]]))

;;(spit "output.txt" (t/table-str [[1 2] [3 4] [5 6]] :style :unicode))

(def TYPES ["mp3" "flac" "wav" "aiff"])

(defn ^:deprecated make-map [triples]
  (reduce (fn [result [a b c]] (update-in result [a b] #(vec (conj % c))))
          (sorted-map)
          triples))

(defn type-row [type]
  (let [empties (vec (repeat (count TYPES) nil))
        dotted-types (map #(format ".%s" %) TYPES)
        pos (.indexOf dotted-types type)]
    (assoc empties pos type)
    ))

(defn expound [triples]
  (map (fn [[artist album type]] (concat [artist album] (type-row type))) triples))

(defn dedup-first-column [rows]
  (-> (reduce (fn [{:keys [result v]} row]
                (if (= v (first row))
                  {:result (conj result
                                 (conj (next row) nil))
                   :v v}
                  {:result (conj result row)
                   :v (first row)}))
              {:result nil :v nil}
              rows)
      :result
      reverse))

;;(dedup-first-column (seq [[1 2 3] [4 5 6] [4 7 8]]))

(let [grammar-matcher (.getPathMatcher
                       (java.nio.file.FileSystems/getDefault)
                       (format "glob:*.{%s}"
                               (clojure.string/join "," TYPES)))
      output (->> "/Volumes/nick/Music/iTunes/iTunes Music"
                  clojure.java.io/file
                  file-seq
                  (filter #(.isFile %))
                  (filter #(.matches grammar-matcher (.getFileName (.toPath %))))
                  (map #(.getAbsolutePath %))
                  (map #(as-> (clojure.string/split % #"/") A
                          (take-last 3 A)
                          (vec A)
                          (update A 2 (fn [f] (re-find #"\.[^.]+$" f) ) )))

                  dedupe
                  sort
                  expound
                  dedup-first-column)]

  ;;(spit "output.yaml" (yaml/generate-string output :dumper-options {:flow-style :block}))
  (binding [*width* (delay 300)]
        (spit "output.txt" (t/table-str (conj output
                                              (vec (concat ["artist" "album"] TYPES)))
                                        :style :unicode))))
