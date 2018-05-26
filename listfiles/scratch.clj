(ns user
  (:require [yaml.core :as yaml]))

(defn make-map [triples]
  (reduce (fn [result [a b c]] (update-in result [a b] #(vec (conj % c))))
          (sorted-map)
          triples))

(let [grammar-matcher (.getPathMatcher
                       (java.nio.file.FileSystems/getDefault)
                       "glob:*.{mp3,mp4,flac,wav,aiff}")
      output (->> "/Volumes/nick/Music/iTunes/iTunes Music"
                  clojure.java.io/file
                  file-seq
                  (filter #(.isFile %))
                  (filter #(.matches grammar-matcher (.getFileName (.toPath %))))
                  (map #(.getAbsolutePath %))
                  (map #(as-> (clojure.string/split % #"/") A
                          (take-last 3 A)
                          (map (fn [i] (nth A i)) [0 2 1])
                          (vec A)
                          (update A 1 (fn [f] (re-find #"\.[^.]+$" f) ) )))

                  dedupe
                  sort
                  make-map)]

  (spit "output.yaml" (yaml/generate-string output :dumper-options {:flow-style :block})))
