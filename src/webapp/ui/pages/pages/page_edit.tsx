import React from "react";
import validator from "@rjsf/validator-ajv6";
import { Box, Heading, Stack, useToast } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../../casualcms/domain/ports";
import { useConfig } from "../../../config";
import { Draft, PageType } from "../../../casualcms/domain/model";
import { ApiErrorUI } from "../../components/error_api";
import { Loader } from "../../components/loader";
import { PageBreadcrumb } from "../../components/breadcrumb";
import { PageEditButtons } from "./page_publish";
import { RichTextEditor } from "../../components/richtext/component";

const Form = withTheme(ChakraUITheme);

export const PageEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = useConfig();
  const token = auth.authenticatedUser?.token || "";
  const [pageType, setPageType] = React.useState<PageType | null>(null);
  const [page, setPage] = React.useState<Draft | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const pagePath = params.get("page") || "";
  const pagePathSplit = pagePath.split("/");
  pagePathSplit.pop();
  const parentPath: string = pagePathSplit.length
    ? pagePathSplit.join("/")
    : "";
  const q = parentPath
    ? new URLSearchParams({ parent: parentPath })
    : new URLSearchParams();

  const toast = useToast();
  React.useEffect(() => {
    async function loadPageType() {
      if (!page) {
        return;
      }
      const rtyp = await config.api.pageType.showPageType(
        token,
        page.metadata.type
      );
      // console.log(rtyp);
      rtyp
        .map((typ: PageType) => setPageType(typ))
        .mapErr((err: ApiError) => setError(err));
      // console.log("setIsLoading");
      setIsLoading(false);
    }
    if (token && page) {
      loadPageType();
    }
    return () => {
      setPageType(null);
      setError(null);
      setIsLoading(true);
    };
  }, [auth, page]);

  React.useEffect(() => {
    async function loadPage() {
      const page = await config.api.page.showDraft(token, pagePath || "");
      // console.log(page)
      page
        .map((page: Draft) => setPage(page))
        .mapErr((err: ApiError) => setError(err));
    }
    if (token) {
      loadPage();
    }
    return () => {
      setPage(null);
      setError(null);
    };
  }, [auth, pagePath]);

  const onsubmit = async (data: any) => {
    if (!page) {
      return;
    }
    const newPage = data.formData;
    await config.api.page.updateDraft(token, page.metadata.path, newPage);
    toast({
      title: "Draft page saved.",
      description: "Don't forget to publish you changes afterall.",
      status: "success",
      duration: 2000,
      isClosable: true,
    });
  };

  if (isLoading) {
    return <Loader label="loading page and page type..." />;
  }

  const widgets = { richtext: RichTextEditor };
  return (
    <Box minW="720px">
      {page && (
        <>
          <Heading>{page.title}</Heading>
          <PageBreadcrumb page={page} />
        </>
      )}

      <ApiErrorUI error={error} />
      <Box maxW="720px">
        {pageType && page && (
          <Form
            schema={pageType.schema}
            uiSchema={pageType.uiSchema}
            widgets={widgets}
            formData={page}
            validator={validator}
            // onChange={() => console.log("changed")}
            onSubmit={onsubmit}
            // onError={() => console.log("errors")}
          />
        )}
      </Box>
      <Stack paddingTop={5} direction="row" align="right">
        <PageEditButtons token={token} pagePath={pagePath} />
      </Stack>
    </Box>
  );
};
