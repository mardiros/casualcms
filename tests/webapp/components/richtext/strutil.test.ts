import { expect } from "chai";
import { escapeHtml } from "../../../../src/webapp/ui/components/richtext/strutil";

describe("As an html editor, I need to escape HTML inputs", () => {
  describe("escapeHtml", () => {
    it("It escape HTML special chars", async () => {
      const escaped = escapeHtml("<b>\"Lorem\" 'Ipsum'</b><i>dolor sit 'amet'.</i>");
      expect(escaped).equal(
        "&lt;b&gt;&quot;Lorem&quot; &#039;Ipsum&#039;&lt;/b&gt;&lt;i&gt;" +
          "dolor sit &#039;amet&#039;.&lt;/i&gt;",
      );
    });
  });
});
