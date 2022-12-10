import { expect } from "chai";

import {
  fromHtml,
  defaultModel,
} from "../../../../src/webapp/ui/components/richtext/parser";

describe("Convert Html to SlateModel", () => {
  it("Parse empty textgenerate the empty paragraph", () => {
    const mdl = fromHtml("");
    expect(mdl).eql(defaultModel());
  });

  it("Parse paragraph extract the text", () => {
    const mdl = fromHtml("<p>My lazy dog</p>");
    expect(mdl).eql([
      {
        children: [
          {
            type: "TEXT",
            text: "My lazy dog",
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
          },
        ],
        type: "paragraph",
      },
    ]);
  });

  it("Parse paragraph extract bold text", () => {
    const mdl = fromHtml("<p>My <strong>lazy</strong> dog</p>");
    expect(mdl).eql([
      {
        children: [
          {
            type: "TEXT",
            text: "My ",
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
          },
          {
            type: "TEXT",
            text: "lazy",
            bold: true,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
          },
          {
            type: "TEXT",
            text: " dog",
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
          },
        ],
        type: "paragraph",
      },
    ]);
  });

  it("Parse titles and paragraphs", () => {
    const mdl = fromHtml(
      "<h1>Title</h1><p>My lazy dog</p><h2>Subtitle</h2><p>ha ha!</p>"
    );
    expect(mdl).eql([
      {
        type: "h1",
        children: [
          {
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
            type: "TEXT",
            text: "Title",
          },
        ],
      },
      {
        type: "paragraph",
        children: [
          {
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
            type: "TEXT",
            text: "My lazy dog",
          },
        ],
      },
      {
        type: "h2",
        children: [
          {
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
            type: "TEXT",
            text: "Subtitle",
          },
        ],
      },
      {
        type: "paragraph",
        children: [
          {
            bold: undefined,
            italic: undefined,
            underline: undefined,
            strikethrough: undefined,
            type: "TEXT",
            text: "ha ha!",
          },
        ],
      },
    ]);
  });
  it("Parse unordered list", () => {
    const mdl = fromHtml("<ul><li>Dog</li><li>Cat</li><li>Lezard</li></ul>");
    expect(mdl).eql([
      {
        type: "ul",
        children: [
          {
            type: "li",
            children: [
              {
                bold: undefined,
                italic: undefined,
                underline: undefined,
                strikethrough: undefined,
                type: "TEXT",
                text: "Dog",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                bold: undefined,
                italic: undefined,
                underline: undefined,
                strikethrough: undefined,
                type: "TEXT",
                text: "Cat",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                bold: undefined,
                italic: undefined,
                underline: undefined,
                strikethrough: undefined,
                type: "TEXT",
                text: "Lezard",
              },
            ],
          },
        ],
      },
    ]);
  });

  it("Parse ordered list", () => {
    const mdl = fromHtml("<ol><li>Dog</li><li>Cat</li><li>Lezard</li></ol>");
    expect(mdl).eql([
      {
        type: "ol",
        children: [
          {
            type: "li",
            children: [
              {
                bold: undefined,
                italic: undefined,
                underline: undefined,
                strikethrough: undefined,
                type: "TEXT",
                text: "Dog",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                bold: undefined,
                italic: undefined,
                underline: undefined,
                strikethrough: undefined,
                type: "TEXT",
                text: "Cat",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                bold: undefined,
                italic: undefined,
                underline: undefined,
                strikethrough: undefined,
                type: "TEXT",
                text: "Lezard",
              },
            ],
          },
        ],
      },
    ]);
  });
});
