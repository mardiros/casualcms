import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { PartialDraft } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/hooks";
import { Link, Navigate } from "react-router-dom";
import { Result } from "neverthrow";
import { Loader } from "../layout/loader";

export const HomePage: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [pages, setPages] = React.useState<PartialDraft[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    async function loadPages() {
      let pages: Result<PartialDraft[], ApiError>;
      pages = await config.api.page.listDrafts(token, null);
      pages
        .map((pages: PartialDraft[]) => setPages(pages))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadPages();
    }
    return function cleanup() {};
  }, [auth]);

  if (isLoading) {
    return <Loader label="preparing data..." />;
  }

  if (!error && pages.length) {
    return <Navigate to="/admin/pages" replace />;
  }
  return (
    <>
      <Heading>Welcome {auth.authenticatedUser?.username}!</Heading>
      <Box>
        <Link to="/admin/pages/new">Create my first page</Link>.
      </Box>
    </>
  );
};
